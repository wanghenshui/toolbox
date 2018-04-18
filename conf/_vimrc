source $VIMRUNTIME/vimrc_example.vim
source $VIMRUNTIME/mswin.vim
behave mswin

set diffexpr=MyDiff()
function MyDiff()
  let opt = '-a --binary '
  if &diffopt =~ 'icase' | let opt = opt . '-i ' | endif
  if &diffopt =~ 'iwhite' | let opt = opt . '-b ' | endif
  let arg1 = v:fname_in
  if arg1 =~ ' ' | let arg1 = '"' . arg1 . '"' | endif
  let arg2 = v:fname_new
  if arg2 =~ ' ' | let arg2 = '"' . arg2 . '"' | endif
  let arg3 = v:fname_out
  if arg3 =~ ' ' | let arg3 = '"' . arg3 . '"' | endif
  if $VIMRUNTIME =~ ' '
    if &sh =~ '\<cmd'
      if empty(&shellxquote)
        let l:shxq_sav = ''
        set shellxquote&
      endif
      let cmd = '"' . $VIMRUNTIME . '\diff"'
    else
      let cmd = substitute($VIMRUNTIME, ' ', '" ', '') . '\diff"'
    endif
  else
    let cmd = $VIMRUNTIME . '\diff'
  endif
  silent execute '!' . cmd . ' ' . opt . arg1 . ' ' . arg2 . ' > ' . arg3
  if exists('l:shxq_sav')
    let &shellxquote=l:shxq_sav
  endif
endfunction

"显示文本处理模式

set showmode

"使用vim自己的键盘模式,而不是兼容vi的模式

set nocompatible

"设置配色方案

colorscheme torte

"处理未保存或者只读文件时,给出提示

set confirm

"文件保存编码

set fileencoding=utf-8 

"文件打开时使用的编码

set fileencodings=utf-8,gb2312,gbk,gb18030,cp936 

" show linenumber

set number

"开启语法高亮

syntax on

"检测文件类型

filetype on

"开启自动对齐和智能对齐

set autoindent

set smartindent

"开启自动换行

set wrap

"第一行设置tab键为4个空格,第二行设置当行之间交错时使用4个空格

set tabstop=4

set shiftwidth=4

"开启匹配模式(左右符号匹配)

set showmatch

"关闭gui中的toolbar

set guioptions-=T

"在右下角显示光标位置的状态行

set ruler

"开启即时搜索

set incsearch

"高亮搜索结果

 set hlsearch

"显示状态栏(默认值为1,无法显示状态栏)

"set laststatus=2

"开启折叠

set foldenable

"设置折叠方式为语法折叠

set foldmethod=syntax

"设置折叠区域的宽度

set foldcolumn=0

"设置折叠层次

setlocal foldlevel=1

"设置文件格式

set fileformats=unix,dos,mac

"全屏
autocmd GUIEnter * simalt ~x

"对齐线
set cuc
set cul
set ruler

"设置字体
set guifont=Consolas:h14

" backspace and cursor keys wrap to previous/next line

set backspace=indent,eol,start whichwrap+=<,>,[,]

"加载windows下的已有配置

source $VIMRUNTIME/mswin.vim

behave mswin

 

"设置自动备份

if has("vms")

    set nobackup

else

        set backup

endif

