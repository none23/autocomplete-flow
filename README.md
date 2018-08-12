
## Autocomplete-flow

Flow autocompletion for [deoplete](https://github.com/Shougo/deoplete.nvim)

## Installation

This plugin requires neovim (vim8 should work, too) with python.
Minimal working `.vimrc`/`init.vim`:

```vimL
call plug#begin()
  Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
  Plug 'wokalski/autocomplete-flow'
  " For func argument completion
call plug#end()

" deoplete

let g:deoplete#enable_at_startup = 1
let g:autocomplete_flow#insert_paren_after_function = 0

```

## Credits

This is a trimmed down version of [wokalski/autocomplete-flow](https://github.com/wokalski/autocomplete-flow).
