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
function sysinfo { neofetch --colors 3 5 3 3 --ascii_colors 3 3; }

# utility
function pclock { $HOME/bin/scripts/blur_lock.sh; }
function pcsleep { systemctl suspend; }
function night { pclock; pcsleep; }

# corefreq-cli
function corefreq-init { please modprobe corefreqk; please systemctl start corefreqd; }
function cpu-monitor { corefreq-cli; }

# cd
function .. { cd '..'; }
function .... { cd '../..'; }
function ...... { cd '../../..'; }

function usr { cd $HOME/usr; }
function dev { cd  $HOME/usr/dev; }
function tmp { cd $HOME/tmp; }
function doc { cd $HOME/usr/doc; }

# zoom credentials
function zoomc { cat $HOME/tmp/zoomcreds; }

# tda account status (custom via OAuth2.0)
function td-acc {
    TMPDIR=/home/neal/tmp GOOGLE_APPLICATION_CREDENTIALS=/home/neal/usr/dev/trading/cli-stonks/gcpkey-cli-stocks.json /home/neal/usr/dev/trading/cli-stonks/main.py status;
}

alias quote='/home/neal/usr/dev/trading/cli-stonks/main.py quotes '
alias quotes='/home/neal/usr/dev/trading/cli-stonks/main.py quotes '
alias editwl='emacs /home/neal/usr/dev/trading/cli-stonks/config'

# IPython
function ipython { python -m IPython; }
function btop { python -m bpytop; }
alias termdown="python -m termdown"

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
alias dgc='dotgit commit'
alias dgp='dotgit push'

# prompt stuff
PURPLE=$(tput setaf 5)
YELLOW=$(tput setaf 3)
RESET=$(tput sgr0)

# bash prompt
source $HOME/bin/scripts/git_prompt.sh
PS1='\[$YELLOW\]\u\[$RESET\]:\W <\[$PURPLE\]$(gitwd)\[$RESET\]> ζ '
