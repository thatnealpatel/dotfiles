#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias la='ls -a'
alias ll='ls -alh'
alias emacs='emacs -nw'

# memes
alias please='sudo'

# utility
function pclock { $HOME/bin/scripts/blur_lock.sh; }
function pcsleep { systemctl suspend; }
function night { pclock; pcsleep; }

# cd
function .. { cd '..'; }
function .... { cd '../..'; }
function ...... { cd '../../..'; }

# zoom credentials
function zoomc { cat $HOME/tmp/zoomcreds; }


# IPython
function ipython { python -m IPython; }

# git 
alias gs='git status'
alias gc='git commit'
alias gp='git push' 

# git : dotgit for tracking dotfiles.
alias dotgit='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
alias dgs='dotgit status'
function pygitbranch { python $HOME/bin/scripts/get_pwd_branch.py; }

# prompt stuff
WHITE=$(tput setaf 5)
YELLOW=$(tput setaf 4)
RESET=$(tput sgr0)

# bash prompt
PS1='\[$YELLOW\]\u\[$RESET\]:\W <\[$WHITE\]$(pygitbranch)\[$RESET\]> ζ '
