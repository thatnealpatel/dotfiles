# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
from typing import List  # noqa: F401

from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

# COLORS
MY_YELLOW = "#fba922"

# KEY MAPPINGS
MOD = "mod4"
CTRL = "control"
ALT = "mod1"
SHIFT = "shift"

# CONSTANTS
DEFAULT_SINK = 2 # alsa_output.pci-0000_0a_00.4.analog-stereo -- @DEFAULT_SINK@

# ADD TO START UP HOOK:
# "feh --no-fehbg --bg-fill '/home/neal/usr/img/wallpapers/minimal_mountains2.jpg'"



#@subscribe.restart(func) # restart hook for saving current layouts
#@subscribe.startup_complete(func) # start hook for loading layouts
#@subscribe.startup_once(func) # initial singular start up once 



TERMINAL = guess_terminal()

GROUP_CONFIGURATION = [
    ("1", {"layout": "column", "label": "CODE"}),
    ("2", {"layout": "column", "label": "CHAT"}),
    ("3", {"layout": "column", "label": "HTTP"}),
    ("4", {"layout": "floating", "label": "MEET"}),
    ("5", {"layout": "floating", "label": "GAME"}),
    ("6", {"layout": "floating", "label": "IBKR"}),
    ("7", {"layout": "column"}),
    ("8", {"layout": "column"}),
]


screeshot_full_cmd = "scrot 'screenshot_%Y%m%d_%H%M%S.png' -e 'mkdir -p ~/usr/img/screenshots/ && mv $f ~/usr/img/screenshots/ && xclip -selection clipboard -t image/png -i ~/usr/img/screenshots/`ls -1 -t ~/usr/img/screenshots | head -1`'"
screenshot_select_cmd = "scrot -s 'screenshot_%Y%m%d_%H%M%S.png' -e 'mkdir -p ~/usr/img/screenshots/ && mv $f ~/usr/img/screenshots/ && xclip -selection clipboard -t image/png -i ~/usr/img/screenshots/`ls -1 -t ~/usr/img/screenshots | head -1`'"

keys = [
    # Switch between windows
    Key([MOD], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([MOD], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([MOD], "j", lazy.layout.down(), desc="Move focus down"),
    Key([MOD], "k", lazy.layout.up(), desc="Move focus up"),
    Key([MOD], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([MOD, SHIFT], "h", lazy.layout.shuffle_left(),desc="Move window to the left"),
    Key([MOD, SHIFT], "l", lazy.layout.shuffle_right(),desc="Move window to the right"),
    Key([MOD, SHIFT], "j", lazy.layout.shuffle_down(),desc="Move window down"),
    Key([MOD, SHIFT], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([MOD, "control"], "h", lazy.layout.grow_left(),desc="Grow window to the left"),
    Key([MOD, "control"], "l", lazy.layout.grow_right(),desc="Grow window to the right"),
    Key([MOD, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([MOD, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([MOD], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([MOD, SHIFT], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    Key([MOD], "Return", lazy.spawn(TERMINAL), desc="Launch terminal"),

    # QTILE CORE
    Key([MOD, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([MOD, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([MOD], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([MOD], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([MOD, SHIFT], "q", lazy.window.kill(), desc="Kill focused window"),

    # MUSIC
    Key([CTRL, ALT], "Left", lazy.spawn("playerctl previous")),
    Key([CTRL, ALT], "Right", lazy.spawn("playerctl next")),
    Key([CTRL, ALT], "Down", lazy.spawn("playerctl play-pause")),
    Key([MOD], "minus", lazy.spawn(f"pactl set-sink-volume {DEFAULT_SINK} -10%")),
    Key([MOD], "equal", lazy.spawn(f"pactl set-sink-volume {DEFAULT_SINK} +10%")),

    # SCROT
    Key([], "Print", lazy.spawn(screeshot_full_cmd)),
    Key([SHIFT], "Print", lazy.spawn(screenshot_select_cmd)),

    # SYS
    Key([MOD], "0", lazy.spawn("/home/neal/bin/scripts/blur_lock.sh")),
    Key([MOD, CTRL], "0", lazy.spawn("/home/neal/bin/scripts/pcsleep.sh")),
    
]

groups = [Group(name, **kwargs) for name, kwargs in GROUP_CONFIGURATION]
# groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([MOD], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # # mod1 + shift + letter of group = switch to & move focused window to group
        # Key([MOD, SHIFT], i.name, lazy.window.togroup(i.name, switch_group=True),
        #     desc="Switch to & move focused window to group {}".format(i.name)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        Key([MOD, SHIFT], i.name, lazy.window.togroup(i.name),
            desc="move focused window to group {}".format(i.name)),
    ])

floating_config = {
    "border_focus": MY_YELLOW,
    "border_normal": "#000000",
    "border_width": 1,
}

column_config = {
    "border_focus": MY_YELLOW,
    "border_normal": "#000000",
    "border_width": 1,
    "margin": [0]*4,
    "num_columns": 3,
    "border_focus_stack": "ff4040",

}


layouts = [
    layout.Columns(**column_config),
    layout.Max(),
    layout.Floating(**floating_config),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=3),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font='mono',
    fontsize=12,
    padding=5,
)
extension_defaults = widget_defaults.copy()

chord_config = {
    "chords_colors": {'launch': ("#ff0000", "#ffffff")},
    "name_transform": lambda name: name.upper(),
}


def get_quotes():
    stream_in = os.popen("/home/neal/usr/proj/trading/cli-stonks/main.py qtile-watchlist").read()
    return f"{stream_in}"


current_layout_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
}


group_box_config = {
    "background": MY_YELLOW,
    "active": "2e2e2e",
    "highlight_method": "line",
    "highlight_color": [MY_YELLOW, "b5760d"],
    "foreground": "ffffff",
    "borderwidth": 0,
    "hide_unused": True,
    "disable_drag": True,
}


poll_config = {
    "func": get_quotes,
    "update_interval": 1,
    "foreground": MY_YELLOW,
    "background": "2e2e2e",
    "fmt": "\n{}"
}

prompt_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
    "cursor_color": "2e2e2e",
    "prompt": "run: " 
}

cpu_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
}

memory_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
    "format": "RAM {MemUsed:.0f}M",
    "measure_mem": "G"
}

df_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
    "update_interval": 30,
    "visible_on_warn": False,
    "format": "/neal {f}{m}"
}

check_updates_config = {
    "background": MY_YELLOW,
    "colour_have_updates": "2e2e2e",
    "colour_no_updates": "2e2e2e",
}

net_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
    "format": "D[{down}] U[{up}]",
}

clock_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
    "format": "%a %d %b %Y %H.%M.%S",
}

sep_config = {
    "background": MY_YELLOW,
    "foreground": "2e2e2e",
}

###
bluetooth_config = {
    "font": "mono"
}
###

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(**current_layout_config),
                widget.Spacer(length=2),
                widget.GroupBox(**group_box_config),
                widget.Spacer(length=2),
                widget.Prompt(**prompt_config),
                # widget.Chord(**chord_config),
                widget.Spacer(length=bar.STRETCH),
                widget.GenPollText(**poll_config),
                widget.Spacer(length=bar.STRETCH),
                widget.Spacer(length=2),
                widget.CPU(**cpu_config),
                widget.Spacer(length=2),
                widget.Memory(**memory_config),
                widget.Spacer(length=2),
                widget.DF(**df_config),
                widget.Spacer(length=2),
                widget.CheckUpdates(**check_updates_config),
                widget.Spacer(length=2),
                widget.Net(**net_config),
                # widget.Notify(),
                # widget.NvidiaSensors(),
                # widget.Volume(), # configured with amixer, not pactl out of the box
                # widget.Wlan(), # requires iwlib
                # widget.Systray(),
                #widget.Bluetooth(**bluetooth_config),
                widget.Spacer(length=2),
                widget.Clock(**clock_config),
                # widget.QuickExit(),
            ],
            25,
            background="2E2E2E",
            # margin=[5, 750, 5, 750],
            opacity=1
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([MOD], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([MOD], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([MOD], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
