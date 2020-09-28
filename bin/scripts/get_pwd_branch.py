#!/usr/bin/python

'''
For use in .bashrc to append current directory's active git branch.
/usr/bin/python -> python3
/usr/bin/python3 -> /usr/bin/python3.8 
'''

from subprocess import check_output

# dotgit -> '/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
res = '~'
git = check_output(['ls', '-a']).decode('utf8')
if git.find('.git ') > 0: # we found a .git repo
    res = check_output(['git', 'branch', '--show-current']).decode('utf8') #.split("* ")[1]
elif git.find('.dotfiles') > 0:
	res = '.dotfiles' # show the flag for .git -> .dotfiles (--bare) repo.
print(res,end='')
