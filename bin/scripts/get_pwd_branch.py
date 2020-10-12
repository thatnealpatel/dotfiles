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

# a few exceptions to substrings of 'git'
except_one = git.find('.gitconfig') < 0
except_two = git.find('nealdotpy.github.io') < 0

if git.find('.git ') > 0 or (git.find('.git') > 0 and except_one and except_two): # we found a .git repo
    branch = check_output(['git', 'branch', '--show-current']).decode('utf8')
    res = f'git:{branch}' #.split("* ")[1]
elif git.find('.dotfiles') > 0:
	res = 'dotgit:master' # show the flag for .git -> .dotfiles (--bare) repo.
print(res,end='')
