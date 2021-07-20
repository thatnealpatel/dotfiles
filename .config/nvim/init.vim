call plug#begin('~/.nvim/plugged')

" Plug 'usr/repo'
Plug 'preservim/nerdtree'
Plug 'jistr/vim-nerdtree-tabs'
Plug 'preservim/nerdcommenter'
Plug 'crusoexia/vim-monokai'
Plug 'patstockwell/vim-monokai-tasty'
Plug 'itchyny/lightline.vim'
Plug 'neoclide/coc.nvim', {'branch': 'release'}

call plug#end()

filetype plugin indent on " filetypes auto-detected
syntax on " enable syntax highlighting
"colorscheme vim-monokai-tasty
colorscheme monokai

set runtimepath^=~/.vim runtimepath+=~/.vim/after
let &packpath = &runtimepath

augroup nerdtree_open
    autocmd!
    autocmd VimEnter * NERDTree | wincmd p
    autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() |
        \ quit | endif
    autocmd BufEnter * if bufname('#') =~ 'NERD_tree_\d\+' && bufname('%') !~ 'NERD_tree_\d\+' && winnr('$') > 1 |
        \ let buf=bufnr() | buffer# | execute "normal! \<C-W>w" | execute 'buffer'.buf | endif
    autocmd BufWinEnter * silent NERDTreeMirror
augroup END

nnoremap <leader>n :NERDTreeFocus<CR>
nnoremap <C-n> :NERDTree<CR>
nnoremap <C-t> :NERDTreeToggle<CR>
nnoremap <C-f> :NERDTreeFind<CR>autocmd 

let NERDTreeShowHidden=1

source ~/.vimrc
