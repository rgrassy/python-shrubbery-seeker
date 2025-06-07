# Make sure you have an 'audio' folder in the same directory as this script,
# containing all required .wav files for the game to run (see README for file names).

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"       # Prevents pygame from opening a window
os.environ["SDL_AUDIODRIVER"] = "directsound" # Ensures standard Windows audio output

import tkinter as tk
import random
from functools import partial
import pygame
import itertools

# === Sound setup ===

def make_shuffled_cycle(files):
    """
    Create an infinite shuffled cycle from a list of files.
    Used to avoid repeating the same sound in sequence.
    """
    items = list(files)
    random.shuffle(items)
    return itertools.cycle(items)

def reshuffle_cycle(files, cycle_holder):
    """
    Reshuffle the sound cycle in place.
    """
    cycle_holder[0] = make_shuffled_cycle(files)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Sound file lists
SND_START_FILES = [
    "audio/start_mp_repressed.wav"
]
SND_FLIP_FILES = [
    "audio/vfast-whoosh.wav"
]

# Initialize infinite cycles for sound playback
start_cycle = [make_shuffled_cycle(SND_START_FILES)]
flip_cycle = [make_shuffled_cycle(SND_FLIP_FILES)]

def play_random_start_sound():
    """
    Play the 'start' sound effect when the game starts.
    """
    pygame.mixer.stop()
    snd_file = next(start_cycle[0])
    print("Playing start:", snd_file)
    try:
        pygame.mixer.Sound(snd_file).play()
    except Exception as e:
        print(f"Error playing sound {snd_file}: {e}")

def play_random_flip_sound():
    """
    Play the 'flip' sound during the animation sequence.
    """
    pygame.mixer.stop()
    snd_file = next(flip_cycle[0])
    print("Playing flip:", snd_file)
    try:
        pygame.mixer.Sound(snd_file).play()
    except Exception as e:
        print(f"Error playing sound {snd_file}: {e}")

# === Alternating sound toggles ===

# Toggle variable for alternating sounds on "Generate New"
gen_sound_toggle = 0
GEN_SOUNDS = [
    "audio/pb_inconceivable.wav",
    "audio/pb_as_you_wish.wav"
]
def play_alternating_gen_sound():
    """
    Alternate between two generation sounds for variety.
    """
    global gen_sound_toggle
    pygame.mixer.stop()
    snd_file = GEN_SOUNDS[gen_sound_toggle]
    print("Playing generate:", snd_file)
    try:
        pygame.mixer.Sound(snd_file).play()
    except Exception as e:
        print(f"Error playing sound {snd_file}: {e}")
    gen_sound_toggle = (gen_sound_toggle + 1) % len(GEN_SOUNDS)

# Toggle variable for alternating end sounds (on fortune reveal)
end_sound_toggle = 0
END_SOUNDS = [
    "audio/mehran_keep_on_coding.wav",    # Plays first
    "audio/chrisp_beautiful_process.wav"  # Plays second
]
def play_alternating_end_sound():
    """
    Alternate between two end sounds when a fortune is revealed.
    """
    global end_sound_toggle
    pygame.mixer.stop()
    snd_file = END_SOUNDS[end_sound_toggle]
    print("Playing end:", snd_file)
    try:
        pygame.mixer.Sound(snd_file).play()
    except Exception as e:
        print(f"Error playing sound {snd_file}: {e}")
    end_sound_toggle = (end_sound_toggle + 1) % len(END_SOUNDS)

# === GUI/game logic ===

# Constants for window size and shape positioning
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
cx, cy, R = 200, 200, 100  # center and "radius" for drawing shapes

# Game state globals
colors = []               # Holds 4 unique colors for the round
number_options = []       # Holds 4 numbers (1-9) for the round
game_phase = "waiting_start"  # Current phase of the game
fortune_toggle = 0        # Index for cycling through fortunes

# The list of fortunes shown in order (cycled through)
FORTUNES = [
    "You shall find your shrubbery—and it will be most impressive.",
    "On your quest, remember: it’s only a flesh wound!",
    "Spam, spam, spam, eggs and spam. Where's Mehran?",
    "A royal decree: Victory is nigh!",
    "You are worthy of Excalibur—lead on!",
    "Hop to it—beware the rabbit!",
    "Minstrels rejoice—your tale is one of bravery!",
    "None shall pass! Killer Bunny broke its leg, bled all over Easter Egg."
]

def unbind_fortune_number_clicks():
    """
    Remove any event bindings from the fortune number triangles,
    preventing multiple clicks or clicks during the wrong phase.
    """
    for idx in range(4):
        tag = f"fortune_num_{idx}"
        canvas.tag_unbind(tag, "<Button-1>")

def start_game():
    """
    Reset and display the starting game UI.
    Shows the title, description, and control buttons.
    """
    play_random_start_sound()
    global game_phase
    unbind_fortune_number_clicks()
    canvas.delete("all")
    canvas.config(bg="white")
    canvas.create_text(WINDOW_WIDTH // 2, 20, text="Python Shrubbery Seeker",
                      font=("Arial", 20), tags="title")
    canvas.create_text(WINDOW_WIDTH // 2, 50,
                      text="Cootie catcher fortunes—no shrubbery required!",
                      font=("Arial", 12, "italic"), tags="description")
    # Buttons for generating a new round or starting play
    generate_btn = tk.Button(root, text="Generate New", command=lambda: generate_new(play_sound=True))
    canvas.create_window(450, 85, window=generate_btn, tags="btn")
    play_btn = tk.Button(root, text="Play", command=play_game)
    canvas.create_window(450, 125, window=play_btn, tags="btn")
    game_phase = "waiting_generate"

def generate_new(play_sound=True):
    """
    Generate a new random set of colors and draw the rhombus on the canvas.
    """
    if play_sound:
        play_alternating_gen_sound()
    unbind_fortune_number_clicks()
    global colors, number_options, game_phase
    # Remove all relevant old shapes and UI from previous round
    canvas.delete("rhombus")
    canvas.delete("colorCircles")
    canvas.delete("options")
    canvas.delete("prompt")
    canvas.delete("squareShape")
    canvas.delete("triangleCircles")
    for idx in range(4):
        canvas.delete(f"fortune_num_{idx}")
    canvas.delete("fortune")
    canvas.delete("again_btn")
    # Draw the rhombus (diamond) shape
    points = [cx, cy - R, cx + R, cy, cx, cy + R, cx - R, cy]
    canvas.create_polygon(points, outline="black", fill="white", tags="rhombus", width=3)
    canvas.create_line(cx, cy - R, cx, cy + R, fill="black", tags="rhombus", width=3)
    canvas.create_line(cx - R, cy, cx + R, cy, fill="black", tags="rhombus", width=3)
    # Choose four unique colors and draw colored circles inside the rhombus
    palette = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "cyan"]
    colors = random.sample(palette, 4)
    centroids = [
        (cx - R/3, cy - R/3), (cx + R/3, cy - R/3),
        (cx - R/3, cy + R/3), (cx + R/3, cy + R/3)
    ]
    for idx, (x, y) in enumerate(centroids):
        r = 20
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=colors[idx], outline="black",
                           tags=("colorCircles", f"circle_{idx}"))
    game_phase = "waiting_play"

def play_game():
    """
    Initiate the color selection phase after "Play" is clicked.
    """
    global game_phase
    if game_phase != "waiting_play":
        return
    canvas.delete("fortune")
    canvas.delete("again_btn")
    canvas.delete("prompt")
    canvas.delete("options")
    # Display color pick options as circles
    canvas.create_text(450, cy - 30, text="Pick a color", font=("Arial", 16), tags="prompt")
    start_y = cy + 5
    r_option = int(20 * 0.9)
    for idx, color in enumerate(colors):
        x = 450
        y = start_y + idx * 50
        tag = f"option_{idx}"
        canvas.create_oval(x - r_option, y - r_option, x + r_option, y + r_option,
                           fill=color, outline="black", tags=("options", tag))
        # Bind click to color selection
        canvas.tag_bind(tag, "<Button-1>", lambda event, i=idx: select_color(i))
    game_phase = "waiting_color"

def select_color(idx):
    """
    Called when the user selects a color.
    Generates random numbers and moves to the next phase.
    """
    global number_options, game_phase
    if game_phase != "waiting_color":
        return
    number_options = random.sample(range(1, 10), 4)  # 4 unique numbers from 1-9
    draw_square_grid(number_options)
    show_pick_number(number_options)
    game_phase = "waiting_number"

def draw_square_grid(numbers=None, enable_fortune_clicks=False):
    """
    Draws a square grid, internal triangle decorations, and optionally numbers
    on the inner triangles for picking a fortune.
    """
    canvas.delete("rhombus")
    canvas.delete("colorCircles")
    canvas.delete("prompt")
    canvas.delete("options")
    canvas.delete("squareShape")
    canvas.delete("triangleCircles")
    for idx in range(4):
        canvas.delete(f"fortune_num_{idx}")
    canvas.delete("fortune")
    canvas.delete("again_btn")
    # Draw the main square
    x0, y0 = cx - R, cy - R
    x1, y1 = cx + R, cy + R
    canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white",
                           tags="squareShape", width=3)
    # Draw intersecting lines for triangle patterns
    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2
    canvas.create_line(mid_x, y0, mid_x, y1, fill="black", tags="squareShape", width=3)
    canvas.create_line(x0, mid_y, x1, mid_y, fill="black", tags="squareShape", width=3)
    canvas.create_line(mid_x, y0, x0, mid_y, fill="black", tags="squareShape", width=3)
    canvas.create_line(mid_x, y0, x1, mid_y, fill="black", tags="squareShape", width=3)
    canvas.create_line(x0, mid_y, mid_x, y1, fill="black", tags="squareShape", width=3)
    canvas.create_line(x1, mid_y, mid_x, y1, fill="black", tags="squareShape", width=3)
    # Outer triangles for color fill
    t1 = [(mid_x, y0), (x0, y0), (x0, mid_y)]
    t4 = [(mid_x, y0), (x1, y0), (x1, mid_y)]
    t5 = [(x0, mid_y), (x0, y1), (mid_x, y1)]
    t8 = [(x1, mid_y), (x1, y1), (mid_x, y1)]
    triangles = [t1, t4, t5, t8]
    r = 15
    for idx, tri in enumerate(triangles):
        cx_tri = (tri[0][0] + tri[1][0] + tri[2][0]) / 3
        cy_tri = (tri[0][1] + tri[1][1] + tri[2][1]) / 3
        canvas.create_oval(cx_tri - r, cy_tri - r, cx_tri + r, cy_tri + r,
                          fill=colors[idx], outline="black", tags="triangleCircles")
    if numbers:
        # Inner triangles for displaying numbers
        t2 = [(mid_x, y0), (x0, mid_y), (mid_x, mid_y)]
        t3 = [(mid_x, y0), (mid_x, mid_y), (x1, mid_y)]
        t6 = [(mid_x, mid_y), (x0, mid_y), (mid_x, y1)]
        t7 = [(mid_x, mid_y), (mid_x, y1), (x1, mid_y)]
        triangles_nums = [t2, t3, t6, t7]
        for idx, tri in enumerate(triangles_nums):
            cx_tri = (tri[0][0] + tri[1][0] + tri[2][0]) / 3
            cy_tri = (tri[0][1] + tri[1][1] + tri[2][1]) / 3
            tag = f"fortune_num_{idx}"
            canvas.create_text(cx_tri, cy_tri, text=str(numbers[idx]),
                              font=("Arial", 16, "bold"), tags=tag)
            # Bind click event for fortune reveal if enabled
            if enable_fortune_clicks:
                canvas.tag_bind(tag, "<Button-1>", partial(on_triangle_number_click, idx))

def show_pick_number(numbers):
    """
    Display number options on the side for the user to pick after color selection.
    """
    canvas.delete("prompt")
    canvas.delete("options")
    canvas.create_text(450, cy - 30, text="Pick a number", font=("Arial", 16), tags="prompt")
    start_y = cy + 5
    for idx, num in enumerate(numbers):
        x = 450
        y = start_y + idx * 50
        tag = f"num_option_{idx}"
        canvas.create_text(x, y, text=str(num), font=("Arial", 16, "bold"), tags=("options", tag))
        canvas.tag_bind(tag, "<Button-1>", lambda event, i=idx: select_number(numbers[i]))

def select_number(number):
    """
    When a number is picked, begin the flip animation and proceed to fortune reveal.
    """
    global game_phase
    if game_phase != "waiting_number":
        return
    canvas.delete("prompt")
    canvas.delete("options")
    animate_flip(0, number, lambda: show_final_pick_message())

def animate_flip(count, total_flips, end_callback):
    """
    Animate a flipping effect by alternating grid redraws and background color.
    """
    play_random_flip_sound()
    canvas.config(bg="#e0f7ff")
    canvas.after(120, lambda: after_fade(count, total_flips, end_callback))

def after_fade(count, total_flips, end_callback):
    """
    Continue the flip animation sequence, calling the callback when done.
    """
    canvas.config(bg="white")
    if count % 2 == 0:
        generate_new(play_sound=False)
    else:
        draw_square_grid(number_options)
    if count < total_flips * 2 - 1:
        canvas.after(160, lambda: animate_flip(count+1, total_flips, end_callback))
    else:
        # When animation is complete, enable clicking triangles for fortunes
        draw_square_grid(number_options, enable_fortune_clicks=True)
        global game_phase
        game_phase = "waiting_fortune"
        end_callback()

def show_final_pick_message():
    """
    Inform the user to click a triangle for their fortune.
    """
    canvas.delete("fortune")
    canvas.create_text(
        WINDOW_WIDTH // 2, cy + R + 30,
        text="Pick a number to reveal your fortune!",
        font=("Arial", 16, "italic"),
        tags="fortune",
        width=500
    )

def on_triangle_number_click(num_idx, event):
    """
    Event handler for clicking one of the numbered triangles (to reveal fortune).
    """
    if game_phase == "waiting_fortune":
        reveal_fortune(num_idx)

def reveal_fortune(num_idx):
    """
    Reveal the fortune for the selected triangle.
    Easter Egg: If triangle 2 (index 1) and number is 1 or 9, show the special fortune.
    Otherwise, show the next fortune in the cycle.
    """
    global game_phase, fortune_toggle
    canvas.delete("fortune")
    canvas.delete("btn")
    unbind_fortune_number_clicks()
    for idx in range(4):
        canvas.delete(f"fortune_num_{idx}")

    # --- EASTER EGG LOGIC ---
    # Only if the user selects the second triangle (index 1) AND the number in that triangle is 1 or 9,
    # display the special "Holy Grail" fortune.
    if num_idx == 1 and number_options[1] in (1, 9):
        fortune = "Behold... The Holy Grail of Fortunes! 🏆"
    else:
        # Otherwise, cycle through the fortunes list in order.
        fortune = FORTUNES[fortune_toggle]
        fortune_toggle = (fortune_toggle + 1) % len(FORTUNES)
    root.after(500, play_alternating_end_sound)

    # Display the fortune message on the canvas
    canvas.create_text(
        WINDOW_WIDTH // 2, cy + R + 30, text=fortune,
        font=("Arial", 16, "bold"), tags="fortune", width=500
    )
    show_play_again_btn()
    game_phase = "waiting_generate"

def show_play_again_btn():
    """
    Display a "Play Again" button for the user to restart the game.
    """
    again_btn = tk.Button(root, text="Play Again", command=start_game)
    canvas.create_window(WINDOW_WIDTH // 2, cy + R + 65,
                        window=again_btn, tags="again_btn")

# === TK main loop setup ===

# Main window setup
root = tk.Tk()
root.title("Python Shrubbery Seeker")
root.resizable(False, False)
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="grey")
canvas.pack()
# Display initial Start button in the center
start_btn = tk.Button(root, text="Start", command=start_game)
canvas.create_window(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, window=start_btn)
root.mainloop()
