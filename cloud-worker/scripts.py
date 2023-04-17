import argparse
import contextlib
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


def start():
    run_process('py -m cloud_worker.main')
    
def test():
    parser = argparse.ArgumentParser(
        prog='Run pytest in poetry shell',
    )
    parser.add_argument('--regex', help="runs pytest with the -k flag, which only run tests which match the given substring expression", default='')
    parser.add_argument('--log', help="sets the log level", default='warning')
    
    args = parser.parse_args()
    
    command = 'pytest '
    if args.log:
        command += f'-o log_cli=true -o log_cli_level={args.log} '
    if args.regex:
        command += f'-k {args.regex} '
    log.info(command)
    run_process(command)

def healthcheck():
    run_process('curl --fail http://localhost:8080 || exit 1')
    
def add_pre_commit_hooks():
    hooks = {
        "run_pytest": """printf "running test runner"\npoetry run pytest""",
        'poetry_generate_requirements': """printf  "exporting requirements.txt from poetry.lock"\npoetry export --without-hashes --format=requirements.txt > requirements.txt"""
    }
    
    parser = argparse.ArgumentParser(
        prog='Pre-Commit hook generator',
        description="Generate pre-commit hooks to be ran on each commit"
    )
    parser.add_argument('--create', action='store_true', help="opens a text editor to write the pre-commit hook in")
    
    parser.add_argument('--pytest', action='store_true', help='run pytest test runner')
    parser.add_argument('--poetry-reqs', action='store_true', help='export poetry.lock file to requirements.txt format')
    parser.add_argument('--overwrite', action='store_true', help="overwrite any existing pre-commit files already declared")
    
    args = parser.parse_args()
    log.debug(args)
    
    git_dir = Path(__file__).parent /'.git'/'hooks'
    if not git_dir.exists():
        log.warning('git directory was not found')
        return

    new_precommit_file = git_dir/'pre-commit'
    if not args.overwrite and new_precommit_file.exists():
        log.warning('a pre-commit file already exists')
        return
    
    hook_contents = """#!/bin/sh\nprintf  "Running pre-commit hooks.."\n"""
    
    if args.create:
        with temporary_filename() as file:
            Path(file).write_text(hook_contents)
            run_process(f"notepad {file}")
            hook_contents = Path(file).read_text()

    if args.pytest:
        hook_contents += f"\n{hooks['run_pytest']}"

    if args.poetry_reqs:
        hook_contents += f"\n{hooks['poetry_generate_requirements']}"
        
    new_precommit_file.write_text(hook_contents)
    log.info('pre-commit file created successfully')

@contextlib.contextmanager
def temporary_filename(suffix=None):
    """Context that introduces a temporary file.

    Creates a temporary file, yields its name, and upon context exit, deletes it.
    (In contrast, tempfile.NamedTemporaryFile() provides a 'file' object and
    deletes the file as soon as that file object is closed, so the temporary file
    cannot be safely re-opened by another library or process.)

    Args:
    suffix: desired filename extension (e.g. '.mp4').

    Yields:
    The name of the temporary file.
    """
    tmp_name = ''
    try:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_name = f.name
        f.close()
        yield tmp_name
    finally:
        if tmp_name: os.unlink(tmp_name)
    
def run_process(commands: str):
    """run a process
    use to execute commands such as - python -m pip install"""
    try:
        subprocess.run(commands.split())
    except KeyboardInterrupt:
        log.info('Keyboard Interrupt: Terminating Program')
    except Exception:
        log.exception(commands)