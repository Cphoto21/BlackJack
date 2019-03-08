"""
Create a deck of 52 cards
Shuffle the deck
Ask the Player for their bet
Make sure that the Player's bet does not exceed their available chips
Deal two cards to the Dealer and two cards to the Player
Show only one of the Dealer's cards, the other remains hidden
Show both of the Player's cards
Ask the Player if they wish to Hit, and take another card
If the Player's hand doesn't Bust (go over 21), ask if they'd like to Hit again.
If a Player Stands, play the Dealer's hand. The dealer will always Hit until the Dealer's value meets or exceeds 17
Determine the winner and adjust the Player's chips accordingly
Ask the Player if they'd like to play again
"""
import random
import sys
import logbook

SUITS = ('\u2661', '\u2662', '\u2660', '\u2663')
RANKS = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
VALUES = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10,
          'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
PLAYING = True
APP_LOG = logbook.Logger('App')


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return self.rank + ' of ' + self.suit


class Deck:

    def __init__(self):
        self.deck = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop()


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        # card passed in
        # from Deck.deal() --> single Card(suit,rank)
        self.cards.append(card)
        self.value += VALUES[card.rank]

        if card.rank == 'Ace':
            self.aces += 1

    def adjust_for_aces(self):

        while self.value >= 21 and self.aces >= 1:
            self.value -= 10
            self.aces -= 1


class Chips:
    def __init__(self, total=100):
        self.total = total
        self.bet = 0

    def win_bet(self):
        self.total += self.bet * 2

    def lose_bet(self):
        self.total -= self.bet

    def take_bet(self):
        self.bet = input(f'You have: {self.total}\nHow much would you like to bet on this hand? ')
        if not self.bet:
            APP_LOG.warn('Pressed Return')
            raise ValueError('\nPlease enter a number.\n')

        try:
            self.bet = int(self.bet)
        except ValueError:
            APP_LOG.warn('Not an integer')
            raise ValueError("\nLooks like you did not enter an integer!\n")

        if self.bet not in range(1, self.total+1):
            APP_LOG.warn('Out of range bet')
            raise ValueError('\nSorry you do not have the chips to cover this bet.'
                             '\nOr might have entered a negative number.\n')

        return self.bet


def hit(deck, hand):
    hand.add_card(deck.deal())
    hand.adjust_for_aces()


def hit_or_stand(deck, hand):
    global PLAYING

    x = input('Hit or Stand? ')
    if not x:
        APP_LOG.warn('Pressed Return')
        raise ValueError('\nPlease enter Hit or Stand.\n')

    if x[0].lower() == 'h':
        hit(deck, hand)

    elif x[0].lower() == 's':
        print("\nPlayer Stands!\nDealer's turn.\n")
        PLAYING = False
    else:
        APP_LOG.warn('not Hit or Stand')
        raise ValueError('\nSorry that is not Hit or Stand!\nPlease Enter Hit or Stand!\n')


def show_some(player, dealer):
    print("\nDealer's Hand:")
    print(' <card hidden>')
    print(' ', dealer.cards[1])
    print("\n Player's Hand:", *player.cards, sep='\n ')


def show_all(player, dealer):
    print("\nDealer's Hand:", *dealer.cards, sep='\n ')
    print("Dealer's Hand =", dealer.value)
    print("Player's Hand:", *player.cards, sep='\n ')
    print("Player's Hand =", player.value)


def player_bust(chips):
    print('Player Bust.')
    chips.lose_bet()


def player_wins(chips):
    print('Player Wins!')
    chips.win_bet()


def dealer_bust(chips):
    print('Dealer Bust!')
    chips.win_bet()


def dealer_wins(chips):
    print('Dealer Wins.')
    chips.lose_bet()


def push():
    print('Player and Dealer Tie! PUSH')


def main():
    global PLAYING
    while True:
        # Print an opening statement
        print('-'*50 + '\nWelcome to BlackJack! \nGet as close to 21 as you can without going over!'
              '\nDealer hits until reaching 17. \nAces count as 1 or 11.\n' + '-'*50)
    
        # Create & shuffle the deck, deal two cards to each player
        deck = Deck()
        deck.shuffle()
    
        player_hand = Hand()
        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())
    
        dealer_hand = Hand()
        dealer_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())
    
        # Set up the Player's chips
        player_chips = Chips()

        # Prompt the Player for their bet
        try:
            Chips.take_bet(player_chips)
        except ValueError as ve:
            print(ve)
            continue
    
        # Show cards (but keep one dealer card hidden)
        show_some(player_hand, dealer_hand)
    
        while PLAYING:  # recall this variable from our hit_or_stand function

            player_hand.adjust_for_aces()

            # Prompt for Player to Hit or Stand
            try:
                hit_or_stand(deck, player_hand)
            except ValueError as ve:
                print(ve)
                continue
    
            # Show cards (but keep one dealer card hidden)
            show_some(player_hand, dealer_hand)
    
            # If player's hand exceeds 21, run player_busts() and break out of loop
            if player_hand.value > 21:
                player_bust(player_chips)
                break
    
        # If Player hasn't busted, play Dealer's hand until Dealer reaches 17
        if player_hand.value <= 21:
            while dealer_hand.value < 17:
                hit(deck, dealer_hand)
    
            # Show all cards
            show_all(player_hand, dealer_hand)
    
            # Run different winning scenarios
            if dealer_hand.value > 21:
                dealer_bust(player_chips)
            elif dealer_hand.value < player_hand.value:
                player_wins(player_chips)
            elif dealer_hand.value > player_hand.value:
                dealer_wins(player_chips)
            else:
                push()
    
        # Inform Player of their chips total
        print("\nPlayer's winnings stand at ", player_chips.total)
    
        # Ask to play again
        new_game = input('Would you like to play again? \nEnter "Y" or "N": ')
    
        if new_game[0].lower() == 'y':
            PLAYING = True
            continue
        else:
            APP_LOG.notice('Ended Game')
            print('Thank you for playing!')
            break


def init_logging(filename: str = None):
    level = logbook.TRACE

    if filename:
        logbook.TimedRotatingFileHandler(filename, level=level).push_application()
    else:
        logbook.StreamHandler(sys.stdout, level=level).push_application()

    msg = 'Logging initialized, level: {}, mode: {}'.format(level,
                                                            "stdout mode" if not filename else 'file mode: ' + filename)
    logger = logbook.Logger('Startup')
    logger.notice(msg)


if __name__ == "__main__":
    init_logging('blackjack-app.log')
    main()
