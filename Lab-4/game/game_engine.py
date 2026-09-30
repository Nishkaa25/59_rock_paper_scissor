import math
import random
from collections import Counter

import pygame
from game.button import ChoiceButton


class GameEngine:
    def __init__(self, width, height, target_score=5):
        if not isinstance(target_score, int) or isinstance(target_score, bool) or target_score < 1:
            raise ValueError('target_score must be a positive integer')
        self.width, self.height = width, height
        self.target_score = target_score
        self.choices = ['ROCK', 'PAPER', 'SCISSORS']
        self.history_limit = 20
        self.display_duration = 1800
        self.animation_duration = 550
        self.font_title = pygame.font.SysFont(None, 42)
        self.font_hud = pygame.font.SysFont(None, 27)
        self.font_arena = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 23)
        button_width, button_height, gap = 150, 54, 20
        start_x = (width - 3 * button_width - 2 * gap) // 2
        colors = [(160, 50, 50), (40, 100, 170), (180, 140, 30)]
        hover = [(200, 70, 70), (60, 130, 210), (220, 180, 50)]
        self.buttons = [
            ChoiceButton(move, pygame.Rect(start_x + i * (button_width + gap),
                         height - 79, button_width, button_height), colors[i], hover[i])
            for i, move in enumerate(self.choices)
        ]
        self.reset_match()

    def reset_match(self):
        self.player_score = self.cpu_score = 0
        self.player_choice = self.cpu_choice = None
        self.player_history = []
        self.match_winner = None
        self.state = 'READY'
        self.result_text = 'Make your move!'
        self.result_color = (220, 225, 235)
        self.animation_started = self.round_resolved_time = 0
        self.showing_result = False

    def determine_winner(self, player, cpu):
        if player not in self.choices or cpu not in self.choices:
            raise ValueError('Unknown move')
        if player == cpu:
            return 'TIE'
        rules = {
            ('ROCK', 'SCISSORS'): 'PLAYER',
            ('SCISSORS', 'PAPER'): 'PLAYER',
            ('PAPER', 'ROCK'): 'PLAYER',
            ('SCISSORS', 'ROCK'): 'CPU',
            ('PAPER', 'SCISSORS'): 'CPU',
            ('ROCK', 'PAPER'): 'CPU',
        }
        return rules[(player, cpu)]

    def cpu_weights(self):
        # Mix uniform exploration with counters to empirical past moves.
        if len(self.player_history) < 3:
            return [1 / 3] * 3
        counts = Counter(self.player_history)
        countered = {'ROCK': 'SCISSORS', 'PAPER': 'ROCK', 'SCISSORS': 'PAPER'}
        return [0.25 / 3 + 0.75 * counts[countered[move]] / len(self.player_history)
                for move in self.choices]

    def choose_cpu_move(self):
        return random.choices(self.choices, weights=self.cpu_weights(), k=1)[0]

    def play_round(self, choice):
        if self.state != 'READY':
            return
        if choice not in self.choices:
            raise ValueError('Unknown move')
        self.player_choice = choice
        # Choose using history BEFORE appending the current player choice.
        self.cpu_choice = self.choose_cpu_move()
        self.player_history.append(choice)
        self.player_history = self.player_history[-self.history_limit:]
        self.animation_started = pygame.time.get_ticks()
        self.state = 'ANIMATING'
        self.result_text = 'Rock... Paper... Scissors!'
        self.result_color = (220, 225, 235)

    def resolve_round(self, now):
        if self.state != 'ANIMATING':
            return
        outcome = self.determine_winner(self.player_choice, self.cpu_choice)
        if outcome == 'PLAYER':
            self.player_score += 1
            self.result_text = f'You win! {self.player_choice} beats {self.cpu_choice}.'
            self.result_color = (80, 230, 120)
        elif outcome == 'CPU':
            self.cpu_score += 1
            self.result_text = f'CPU wins! {self.cpu_choice} beats {self.player_choice}.'
            self.result_color = (240, 100, 100)
        else:
            self.result_text = f'Draw! Both picked {self.player_choice}.'
            self.result_color = (240, 210, 80)
        if self.player_score >= self.target_score:
            self.match_winner = 'PLAYER'
        elif self.cpu_score >= self.target_score:
            self.match_winner = 'CPU'
        self.round_resolved_time = now
        self.showing_result = True
        self.state = 'RESULT'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.state == 'GAME_OVER':
            self.reset_match()
        elif self.state == 'READY' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.contains(event.pos):
                    self.play_round(button.choice_name)
                    break

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == 'ANIMATING' and now - self.animation_started >= self.animation_duration:
            self.resolve_round(now)
        elif self.state == 'RESULT' and now - self.round_resolved_time >= self.display_duration:
            self.showing_result = False
            if self.match_winner:
                self.state = 'GAME_OVER'
                self.result_text = 'You are the match champion!' if self.match_winner == 'PLAYER' else 'CPU is the match champion!'
            else:
                self.state = 'READY'
                self.player_choice = self.cpu_choice = None
                self.result_text = 'Make your move!'
                self.result_color = (220, 225, 235)

    def center_text(self, screen, text, font, color, center_x, y):
        surface = font.render(text, True, color)
        screen.blit(surface, (center_x - surface.get_width() // 2, y))

    def draw_icon(self, screen, move, center, color):
        x, y = center
        outline = (235, 239, 247)
        if move == 'ROCK':
            points = [(x - 43, y + 15), (x - 32, y - 25), (x - 8, y - 39),
                      (x + 29, y - 30), (x + 43, y + 5), (x + 20, y + 35), (x - 23, y + 31)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, outline, points, 3)
            pygame.draw.line(screen, outline, (x - 24, y - 8), (x - 8, y - 19), 3)
        elif move == 'PAPER':
            points = [(x - 31, y - 42), (x + 13, y - 42), (x + 32, y - 23),
                      (x + 32, y + 42), (x - 31, y + 42)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, outline, points, 3)
            pygame.draw.lines(screen, outline, False,
                              [(x + 13, y - 42), (x + 13, y - 23), (x + 32, y - 23)], 3)
            for row in (-7, 7, 21):
                pygame.draw.line(screen, outline, (x - 19, y + row), (x + 19, y + row), 3)
        elif move == 'SCISSORS':
            pygame.draw.line(screen, outline, (x - 21, y + 23), (x + 35, y - 40), 9)
            pygame.draw.line(screen, outline, (x + 21, y + 23), (x - 35, y - 40), 9)
            for offset in (-24, 24):
                pygame.draw.circle(screen, color, (x + offset, y + 31), 18)
                pygame.draw.circle(screen, outline, (x + offset, y + 31), 18, 4)
                pygame.draw.circle(screen, (24, 28, 36), (x + offset, y + 31), 8)
            pygame.draw.circle(screen, color, (x, y - 1), 7)
        else:
            self.center_text(screen, '?', self.font_title, color, x, y - 18)

    def render(self, screen):
        screen.fill((24, 28, 36))
        middle = self.width // 2
        self.center_text(screen, 'Rock Paper Scissors', self.font_title, (245, 245, 245), middle, 16)
        self.center_text(screen, f'First to {self.target_score} wins', self.font_hud,
                         (240, 210, 80), middle, 60)
        self.center_text(screen, f'Player: {self.player_score}', self.font_hud,
                         (100, 180, 255), self.width // 4, 100)
        self.center_text(screen, f'CPU: {self.cpu_score}', self.font_hud,
                         (255, 120, 120), self.width * 3 // 4, 100)
        pygame.draw.line(screen, (45, 52, 66), (25, 135), (self.width - 25, 135), 2)
        self.center_text(screen, 'YOU', self.font_hud, (100, 180, 255), self.width // 4, 157)
        self.center_text(screen, 'CPU', self.font_hud, (255, 120, 120), self.width * 3 // 4, 157)
        for center_x, choice, color in ((self.width // 4, self.player_choice, (100, 180, 255)),
                                       (self.width * 3 // 4, self.cpu_choice, (255, 120, 120))):
            center_y = 239
            if self.state == 'ANIMATING':
                elapsed = pygame.time.get_ticks() - self.animation_started
                center_y += int(12 * math.sin(elapsed / 45))
                # Neutral rock shapes hide both selected moves during the shake.
                self.draw_icon(screen, 'ROCK', (center_x, center_y), color)
                label = '...'
            else:
                self.draw_icon(screen, choice, (center_x, center_y), color)
                label = choice or 'Choose a move'
            self.center_text(screen, label, self.font_hud, (225, 225, 230), center_x, 296)
        self.center_text(screen, self.result_text, self.font_arena, self.result_color, middle, 340)
        if self.player_history:
            counts = Counter(self.player_history)
            tendency = max(self.choices, key=lambda move: counts[move])
            history = ' / '.join(f'{move.title()}: {counts[move]}' for move in self.choices)
            self.center_text(screen, f'History (last {len(self.player_history)}): {history}',
                             self.font_small, (175, 185, 202), middle, 379)
            counter = {'ROCK': 'PAPER', 'PAPER': 'SCISSORS', 'SCISSORS': 'ROCK'}[tendency]
            hint = 'CPU warm-up: learning your past choices' if len(self.player_history) < 3 else f'Next-round CPU bias: {counter} counters your frequent {tendency}'
            if len(self.player_history) >= 3 and sum(count == counts[tendency] for count in counts.values()) > 1:
                hint = 'CPU counters past choices; tied favorites share the bias'
            self.center_text(screen, hint, self.font_small, (175, 185, 202), middle, 402)
        else:
            self.center_text(screen, 'Adaptive CPU learns from previous rounds', self.font_small,
                             (175, 185, 202), middle, 389)
        if self.state == 'GAME_OVER':
            self.center_text(screen, 'GAME OVER - Press R to restart', self.font_arena,
                             (240, 210, 80), middle, self.height - 62)
        else:
            for button in self.buttons:
                button.render(screen)
