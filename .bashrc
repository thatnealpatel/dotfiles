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
alias pemacs='sudo emacs -nw'

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

# tda account status (custom via OAuth2.0)
function td-acc { $HOME/bin/scripts/stockbar/stonks.py acc_status; }
alias quote='$HOME/bin/scripts/stockbar/stonks.py get_quote'
alias quotes='$HOME/bin/scripts/stockbar/stonks.py get_quotes'

# IPython
function ipython { python -m IPython; }

# git 
alias gs='git status'
alias gc='git commit'
alias gp='git push' 

function gitwd {
	if __git_ps1 "git:%s" | grep -q 'git'; then
		echo $(__git_ps1 "git:%s")
	elif pwd | grep -qE '(^|\s)/home/neal($|\s)'; then
		echo "dotgit:master"
	else
		echo "git:none"
	fi
}

# git : dotgit for tracking dotfiles.
alias dotgit='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
alias dgs='dotgit status'

# prompt stuff
WHITE=$(tput setaf 5)
YELLOW=$(tput setaf 4)
RESET=$(tput sgr0)

# bash prompt
source $HOME/bin/scripts/git_prompt.sh
PS1='\[$YELLOW\]\u\[$RESET\]:\W <\[$WHITE\]$(gitwd)\[$RESET\]> ζ '
