# Rock Paper Scissors - Lab 4

Original assignment: https://github.com/SETAPESU26/59_rock_paper_scissor

## Run
Python 3.10 or later:
```
python -m pip install -r requirements.txt
python main.py
```

## Completed tasks
1. Corrected all six winning/losing dictionary entries; identical moves draw.
2. First to TARGET_SCORE (default 5) wins. Set TARGET_SCORE in main.py to change X.
   The final round is visible for 1.8 seconds before GAME_OVER. Press R there
   to reset scores and history. Further clicks cannot increase scores.
3. Adaptive CPU uses up to 20 previous accepted player moves. It is random for
   the first three rounds, then mixes 25% uniform randomness with 75% empirical
   counter-move probabilities. CPU selection happens before recording the
   current player choice. No reading the current move to cheat.
4. Procedural rock, paper, and scissors drawings. A 0.55-second shake hides the
   picks until reveal; results stay visible for 1.8 seconds after the reveal.

## Controls
Left-click ROCK, PAPER, or SCISSORS when asked to make a move.
Wait during shake/result display. Press R on GAME_OVER to start another match.

## Submission evidence 
videos/before.mp4 - 10 seconds of the original code showing the reversed result.

videos/after.mp4 - 10 seconds showing corrected rules and the added features.

chat_history.pdf - full actual user/assistant conversation, exported after finishing.

