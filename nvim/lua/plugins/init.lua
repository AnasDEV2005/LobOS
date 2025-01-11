return {
  
  -- Nvchad stuff
  {
    "stevearc/conform.nvim",
    -- event = 'BufWritePre', -- uncomment for format on save
    opts = require "configs.conform",
  },
  {
    "neovim/nvim-lspconfig",
    config = function()
      require "configs.lspconfig"
    end,
  },
  {"nvim-lua/plenary.nvim", lazy = false},
   {
      "nvchad/base46",
      lazy = true,
      build = function()
        require("base46").load_all_highlights()
      end,
   },
   {
     "nvchad/ui",
      lazy = false,
      config = function()
      require "nvchad"
      end
   },

  -- leap
  {
    "ggandor/leap.nvim",
    config = true,
     lazy = false,

  },


-- llm assistant
{ "nvim-neotest/nvim-nio", lazy = false },

  {
    "melbaldove/llm.nvim",
    dependencies = { "nvim-neotest/nvim-nio" }
  },


  -- jupytext/notebook
   {
      "GCBallesteros/jupytext.nvim",
      config = true,
      -- Depending on your nvim distro or config you may need to make the loading not lazy
      lazy=false,
    },

    {
      "GCBallesteros/NotebookNavigator.nvim",
      keys = {
        { "]h", function() require("notebook-navigator").move_cell "d" end },
        { "[h", function() require("notebook-navigator").move_cell "u" end },
        { "<leader>gg", "<cmd>lua require('notebook-navigator').run_cell()<cr>" },
        { "<leader>gm", "<cmd>lua require('notebook-navigator').run_and_move()<cr>" },
      },
      dependencies = {
        "echasnovski/mini.comment",
        "hkupty/iron.nvim", -- repl provider
        -- "akinsho/toggleterm.nvim", -- alternative repl provider
        -- "benlubas/molten-nvim", -- alternative repl provider
        "anuvyklack/hydra.nvim",
      },
      event = "VeryLazy",
      config = function()
        local nn = require "notebook-navigator"
        nn.setup({ activate_hydra_keys = "<leader>gh" })
      end,
    },

    -- harpoon
    {
      "ThePrimeagen/harpoon",
      lazy = false,
      config = function()
      end
    },
    -- right click menu
    { "nvzone/volt" , lazy = true },
--    { "nvzone/menu" , lazy = true },

  -- todo comment
    {
      "folke/todo-comments.nvim",
      lazy = false,
      dependencies = { "nvim-lua/plenary.nvim" },
      opts = {
        -- your configuration comes here
        -- or leave it empty to use the default settings
        -- refer to the configuration section below
      }
    },
    
    -- discord presence
    {'andweeb/presence.nvim', lazy = false, },



}

  -- {
  -- 	"nvim-treesitter/nvim-treesitter",
  -- 	opts = {
  -- 		ensure_installed = {
  -- 			"vim", "lua", "vimdoc",
  --      "html", "css"
  -- 		},
  -- 	},
  -- },
