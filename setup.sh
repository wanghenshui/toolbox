#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
echo "$SCRIPT_DIR"
echo "setup tools for a reinstalled linux system"
echo "sorry for you last fuckup"

echo "install oh-my-ssh..."
if [ ! -d "$HOME"/.oh-my-zsh ]; then
    sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
 #   cp -r  "$SCRIPT_DIR"/conf/.zshrc "$HOME"/.zshrc
fi

#cp -r  "$SCRIPT_DIR"/vim "$HOME"/.vim

echo "ssh key config by your self"

echo "git global config ...."
git config --global color.status auto           # 使 git status -s 命令的输出带有颜色。
git config --global color.diff auto             # 使 git diff 命令的输出带有颜色。
git config --global color.branch auto           # 使 git branch -a 命令的输出带有颜色。
git config --global color.interactive true      # 使 git add -i 命令的输出带有颜色。
git config --global core.autocrlf input         # 别把 CR LF 提交到服务器上。
git config --global push.default simple         # 仅 push 当前分支。
git config --global pull.ff only                # 禁用非 --ff-only 的 pull 操作。
git config --global merge.ff only               # 禁用非 --ff-only 的 merge 操作


echo "golang config..."
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.cn,direct

echo "make data dir"
if [ ! -d "/data" ]; then
  mkdir /data
fi

if [ ! -L "/var/lib/docker" ]; then
  echo "config docker path..."
  mv /var/lib/docker /data/docker
  ln -s /data/docker /var/lib/docker
fi

if [ ! -f "$HOME"/.gdbinit ]; then
  echo "gdbinit config..."
  wget -P ~ https://raw.githubusercontent.com/cyrus-and/gdb-dashboard/master/.gdbinit
fi


echo "python config..."
pip3 install pygments

function install_rust() {
    echo "rust install"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    echo "source $HOME/.cargo/env" >> "$HOME"/.zshrc
    cargo install git-delta
}

read -p "Do you want to install rust" yn
case $yn in
    [Yy]* ) install_rust; break;;
     * ) echo "rust not installed, your choice.";;
esac

function config_git_delta() {
cat << EOF >> "$HOME"/.gitconfig
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true
    
[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
EOF
}

read -p "Do you wish to config git delta" yn
case $yn in
    [Yy]* ) config_git_delta; break;;
     * ) echo "git-delta not config, your choice.";;
esac


echo "third party tool?"
#shellcheck, clang-format

echo "CHECKLIST those something could not automanuly do:"
echo "- add other linux's id_rsa.pub to \"~/.ssh/authorized_keys\""
echo "third party tool?"
echo "update gdb if needed, install on you self"
