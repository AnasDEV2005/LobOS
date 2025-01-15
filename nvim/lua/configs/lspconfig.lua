-- load defaults i.e lua_lsp
require("nvchad.configs.lspconfig").defaults()

local lspconfig = require "lspconfig"

-- EXAMPLE
local servers = { "html", "cssls", "pylsp", "rust_analyzer", "lua_ls", "vimls", "markdown_oxide" }
local nvlsp = require "nvchad.configs.lspconfig"

-- lsps with default config
for _, lsp in ipairs(servers) do
  lspconfig[lsp].setup {
    on_attach = nvlsp.on_attach,
    on_init = nvlsp.on_init,
    capabilities = nvlsp.capabilities,
  }
end


-- Set up rust-analyzer LSP
require'lspconfig'.rust_analyzer.setup{
  settings = {
    ["rust-analyzer"] = {
      cargo = {
        allFeatures = true,
      },
      diagnostic = {
        refreshSupport = false,
      },
      completion = {
        autoimport = { enable = true },           -- Automatically add missing imports
        autoself = { enable = true },             -- Suggest methods/fields with `self.`
        callable = { snippets = "fill_arguments" },  -- Add argument snippets for functions
        fullFunctionSignatures = { enable = true }   -- Show full function signatures in completion
      }
    }
  }
}

-- Set up pylsp (Python LSP)
require'lspconfig'.pylsp.setup{
  settings = {
    pylsp = {
      plugins = {
        pycodestyle = {
          enabled = false
        },
        mccabe = {
          enabled = true
        },
        pyflakes = {
          enabled = true
        },
        jedi_completion = {
          enabled = true,
          include_params = true,
          include_class_objects = true,
          include_function_objects = true,
          fuzzy = true,
          eager = true,
        },
        rope_auto_import = {
          enabled = true,
          completions = {enabled = true},
          code_actions = {enabled = true},
        },
        rope_completion = {enabled = true}
      }
    }
  }
}


-- configuring single server, example: typescript
-- lspconfig.ts_ls.setup {
--   on_attach = nvlsp.on_attach,
--   on_init = nvlsp.on_init,
--   capabilities = nvlsp.capabilities,
-- }
--




