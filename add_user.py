from jinja2 import Environment, FileSystemLoader
from pwd import getpwnam
import subprocess
import shutil
import errno
import os

def write_file(filename, content):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, "w+") as f:
        f.write(content)

username = str(input("username: "))
nickname = str(input("nickname: "))

subprocess.call(['sudo', 'adduser', username])

env = Environment(
    loader=FileSystemLoader("templates"),
)
list_file = ["templates/relay_password.sh", "templates/irc", "templates/.irc_startup.sh", "templates/README", "templates/README.advanced", "templates/MIGRATION", "templates/welcome"]

for f in list_file:
    shutil.copy(f, f"/home/{username}/")

template = env.get_template('alias.conf.j2')
content = template.render(username=username, nickname=nickname)
write_file(f"/home/{username}/.weechat/alias.conf", content)

template = env.get_template('irc.conf.j2')
content = template.render(username=username, nickname=nickname)
write_file(f"/home/{username}/.weechat/irc.conf", content)

template = env.get_template('relay.conf.j2')
# relay_port: the range is thus 61k -> ~62k
content = template.render(password=subprocess.check_output(['openssl', 'passwd', '16']).decode('UTF-8').rstrip(), relay_port=60000+getpwnam(username).pw_uid)
write_file(f"/home/{username}/.weechat/relay.conf", content)

template = env.get_template('weechat.conf.j2')
content = template.render(username=username, nickname=nickname)
write_file(f"/home/{username}/.weechat/weechat.conf", content)

subprocess.call(["sudo", "chown", f"{username}:{username}", "-R", f"/home/{username}/"])
