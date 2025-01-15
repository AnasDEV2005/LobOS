local mark = require("harpoon.mark")
local ui = require("jarpoon.ui")

vim.keymap.set("n", "<leader>mf", mark.add_file)
vim.keymap.set("n", "<leader>mmmmmm", ui.toggle_quick_menu)



