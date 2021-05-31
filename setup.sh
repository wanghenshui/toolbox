#!/bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)

# install oh-my-zsh
#cp -r  $SCRIPT_DIR/vim $HOME/.vim
cp -r  $SCRIPT_DIR/conf/.zshrc $HOME/.zshrc

git config --global color.status auto           # 使 git status -s 命令的输出带有颜色。
git config --global color.diff auto             # 使 git diff 命令的输出带有颜色。
git config --global color.branch auto           # 使 git branch -a 命令的输出带有颜色。
git config --global color.interactive true      # 使 git add -i 命令的输出带有颜色。
git config --global core.autocrlf input         # 别把 CR LF 提交到服务器上。
git config --global push.default simple         # 仅 push 当前分支。
git config --global pull.ff only                # 禁用非 --ff-only 的 pull 操作。
git config --global merge.ff only               # 禁用非 --ff-only 的 merge 操作