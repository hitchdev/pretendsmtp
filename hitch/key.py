from hitchstory import StoryCollection, StorySchema, BaseEngine, HitchStoryException
from hitchstory import validate, expected_exception
from hitchrun import expected
from commandlib import Command, CommandError, python, python_bin
from strictyaml import Str, Map, Seq, Int, Bool, Optional, load
from pathquery import pathquery
from hitchrun import hitch_maintenance
from hitchrun import DIR
from hitchrun.decorators import ignore_ctrlc
from hitchrunpy import ExamplePythonCode, HitchRunPyException
import hitchbuildpy
import dirtemplate
import icommandlib
import smtplib
import json


def project_build(paths, python_version):
    pylibrary = hitchbuildpy.PyLibrary(
        name="py{0}".format(python_version),
        base_python=hitchbuildpy.PyenvBuild(python_version)
                                .with_build_path(paths.share),
        module_name="pretendsmtp",
        library_src=paths.project,
    ).with_requirementstxt(
        paths.key/"debugrequirements.txt"
    ).with_build_path(paths.gen)

    pylibrary.ensure_built()
    return pylibrary


class Engine(BaseEngine):
    """Python engine for running tests."""

    schema = StorySchema(
        given={
            Optional("python version"): Str(),
            Optional("setup"): Str(),
            Optional("code"): Str(),
        },
        info={
            Optional("docs"): Str(),
        },
    )

    def __init__(self, keypath, settings):
        self.path = keypath
        self.settings = settings

    def set_up(self):
        """Set up your applications and the test environment."""
        self.path.state = self.path.gen.joinpath("state")
        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()
        self.path.state.joinpath("mail").mkdir()

        self.build = project_build(
            self.path,
            self.given.get('python version', '3.6.5'),
        )
        self.python = self.build.bin.python
        self.pretendsmtp = self.build.bin.pretendsmtp

        self.example_py_code = ExamplePythonCode(self.python, self.path.state)\
            .with_code(self.given.get('code', ''))\
            .with_setup_code(self.given.get('setup', ''))\
            .with_terminal_size(500, 500)\
            .with_long_strings()

    @validate(args=Seq(Str()))
    def run_pretendsmtp(self, args):
        self.pretendsmtp(*args).in_dir(self.path.state/"mail").run()

    @expected_exception(icommandlib.exceptions.ICommandError)
    @expected_exception(HitchRunPyException)
    def start_server(self, code, and_wait_until_code_prints):
        to_run = self.example_py_code.with_code(code)

        self.running_code = to_run.expect_exceptions().running_code()
        self.running_code.iprocess.wait_until_output_contains(and_wait_until_code_prints)

    @expected_exception(AssertionError)
    def json_file_present(self, filename, content):
        filepath = self.path.state.joinpath(filename)

        assert filepath.exists(), "{0} does not exist".format(filename)

        def processed_json(text):
            snippet = json.loads(text)
            snippet['date'] = "Sat, 26 May 2018 09:00:00 +0000"
            return snippet

        try:
            actual_content = processed_json(filepath.text())

            assert json.loads(content) == actual_content, \
                "Expected:\n {0}\n\nGot:\n\n{1}\n".format(
                    content,
                    filepath.text(),
                )
        except json.decoder.JSONDecodeError:
            try:
                json.loads(content)
            except json.decoder.JSONDecodeError:
                raise AssertionError("EXPECTED:\n\n{0}\n\nis not JSON".format(content))

            try:
                json.loads(filepath.text())
            except json.decoder.JSONDecodeError:
                raise AssertionError("ACTUAL:\n\n{0}\n\nis not JSON".format(
                    json.dumps(actual_content, indent=4)
                ))

        except AssertionError:
            if self.settings.get("rewrite"):
                self.current_step.update(
                    **{"content": json.dumps(actual_content, indent=4)}
                )
            else:
                raise AssertionError("{0} is nonmatching:\n\n{1}".format(
                    json.dumps(actual_content, indent=4), content)
                )

    @expected_exception(AssertionError)
    def html_file_present(self, filename, content):
        filepath = self.path.state.joinpath(filename)

        assert filepath.exists(), "{0} does not exist".format(filename)

        try:
            assert content == filepath.text(), \
              "Expected:\n {0}\n\nGot:\n\n{1}\n".format(
                  content,
                  filepath.text(),
              )
        except AssertionError as error:
            if self.settings.get("rewrite"):
                self.current_step.update(**{"content": filepath.text()})
            else:
                raise AssertionError("{0} is nonmatching:\n\n{1}".format(filename, error))

    @expected_exception(ConnectionRefusedError)
    @expected_exception(smtplib.SMTPServerDisconnected)
    @validate(to_mails=Seq(Str()), port=Int())
    def send_email_to_localhost(self, from_mail, to_mails, message, port):
        smtp_sender = smtplib.SMTP('localhost', port)
        smtp_sender.sendmail(
            from_mail, to_mails, message,
        )

    @expected_exception(ConnectionRefusedError)
    @expected_exception(smtplib.SMTPServerDisconnected)
    @validate(to_mails=Seq(Str()), port=Int())
    def send_email(
        self, port, subject, from_mail, to_mails, plain_message=None, html_message=None,
    ):
        from mailer import Mailer
        from mailer import Message

        message = Message(From=from_mail, To=to_mails, charset="utf-8")
        message.Subject = subject
        message.Html = html_message
        message.Body = plain_message

        sender = Mailer('localhost', port=port)
        sender.send(message)

    def sleep(self, duration):
        import time
        time.sleep(float(duration))

    def pause(self, message="Pause"):
        import IPython
        IPython.embed()

    def on_failure(self, result):
        if hasattr(self, 'running_code'):
            if self.running_code.finished:
                print(self.running_code.iprocess._final_screenshot)
            else:
                print(self.running_code.iprocess.stripshot())

    def on_success(self):
        if self.settings.get("rewrite"):
            self.new_story.save()

    def tear_down(self):
        if hasattr(self, 'running_code'):
            if not self.running_code.finished:
                self.running_code.iprocess.kill()


def _storybook(settings):
    return StoryCollection(pathquery(DIR.key).ext("story"), Engine(DIR, settings))


def _current_version():
    return DIR.project.joinpath("VERSION").bytes().decode('utf8').rstrip()


def _personal_settings():
    settings_file = DIR.key.joinpath("personalsettings.yml")

    if not settings_file.exists():
        settings_file.write_text((
            "engine:\n"
            "  rewrite: no\n"
            "  cprofile: no\n"
            "params:\n"
            "  python version: 3.6.3\n"
        ))
    return load(
        settings_file.bytes().decode('utf8'),
        Map({
            "engine": Map({
                "rewrite": Bool(),
                "cprofile": Bool(),
            }),
            "params": Map({
                "python version": Str(),
            }),
        })
    )


@expected(HitchStoryException)
def bdd(*keywords):
    """
    Run stories matching keywords.
    """
    settings = _personal_settings().data
    _storybook(settings['engine'])\
        .with_params(**{"python version": settings['params']['python version']})\
        .only_uninherited()\
        .shortcut(*keywords).play()


@expected(HitchStoryException)
def rbdd(*keywords):
    """
    Run stories matching keywords and rewrite.
    """
    settings = _personal_settings().data
    _storybook({"rewrite": True})\
        .with_params(**{"python version": settings['params']['python version']})\
        .only_uninherited()\
        .shortcut(*keywords).play()


@expected(HitchStoryException)
def regressfile(filename):
    """
    Run all stories in filename 'filename' in python 2 and 3.

    Rewrite stories if appropriate.
    """
    _storybook({"rewrite": False}).in_filename(filename)\
                                  .with_params(**{"python version": "2.7.10"})\
                                  .filter(lambda story: not story.info['fails on python 2'])\
                                  .ordered_by_name().play()

    _storybook({"rewrite": False}).with_params(**{"python version": "3.5.0"})\
                                  .in_filename(filename).ordered_by_name().play()


@expected(HitchStoryException)
def regression():
    """
    Run regression testing - lint and then run all tests.
    """
    lint()
    storybook = _storybook({}).only_uninherited()
    storybook.with_params(**{"python version": "3.6.3"}).ordered_by_name().play()
    _storybook({}).only_uninherited().with_params(
        **{"python version": "3.5.0"}
    ).ordered_by_name().play()


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("pretendsmtp"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "pretendsmtp"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


@expected(dirtemplate.exceptions.DirTemplateException)
def docgen():
    """
    Build documentation.
    """
    def title(dirfile):
        assert len(dirfile.text().split("---")) >= 3, "{} doesn't have ---".format(dirfile)
        return load(dirfile.text().split("---")[1]).data.get("title", "misc")

    docfolder = DIR.gen/"docs"

    if docfolder.exists():
        docfolder.rmtree(ignore_errors=True)
    docfolder.mkdir()

    template = dirtemplate.DirTemplate(
        "docs", DIR.project/"docs", DIR.gen,
    ).with_files(
        story_md={
            "using/alpha/{0}.md".format(story.info['docs']): {"story": story}
            for story in _storybook({}).ordered_by_name()
            if story.info.get("docs") is not None
        },
    ).with_vars(
        readme=False,
        quickstart=_storybook({})
        .in_filename(DIR.key/"quickstart.story")
        .non_variations()
        .ordered_by_file(),
    ).with_functions(
        title=title
    )
    template.ensure_built()
    print("Docs generated")


@expected(CommandError)
def doctests():
    pylibrary = project_build(DIR, "2.7.10")
    pylibrary.bin.python(
        "-m", "doctest", "-v", DIR.project.joinpath("pretendsmtp", "utils.py")
    ).in_dir(DIR.project.joinpath("pretendsmtp")).run()

    pylibrary = project_build(DIR, "3.5.0")
    pylibrary.bin.python(
        "-m", "doctest", "-v", DIR.project.joinpath("pretendsmtp", "utils.py")
    ).in_dir(DIR.project.joinpath("pretendsmtp")).run()


@ignore_ctrlc
def ipy():
    """
    Run IPython in environment."
    """
    Command(DIR.gen.joinpath("py3.5.0", "bin", "ipython")).run()


def hvenvup(package, directory):
    """
    Install a new version of a package in the hitch venv.
    """
    pip = Command(DIR.gen.joinpath("hvenv", "bin", "pip"))
    pip("uninstall", package, "-y").run()
    pip("install", DIR.project.joinpath(directory).abspath()).run()


def rerun(version="3.5.0"):
    """
    Rerun last example code block with specified version of python.
    """
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        DIR.gen.joinpath("state", "examplepythoncode.py")
    ).in_dir(DIR.gen.joinpath("state")).run()


def black():
    python_bin.black(DIR.project / "pretendsmtp").run()
