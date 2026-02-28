class UltraSafeMode:
    def __init__(self, balance):
        self.start_balance = balance
        self.balance = balance
        self.bet = balance * 0.05
        self.stop_loss = balance * 0.90
        self.stop_gain = balance * 1.15
        self.consecutive_losses = 0
        self.max_losses = 2

    def update_balance(self, new_balance):
        self.balance = new_balance

        if self.balance <= self.stop_loss:
            return "STOP_LOSS"

        if self.balance >= self.stop_gain:
            return "STOP_GAIN"

        return "CONTINUE"

    def register_result(self, win):
        if win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1

        if self.consecutive_losses >= self.max_losses:
            return "STOP_2_LOSSES"

        return "CONTINUE"

    def get_bet_amount(self):
        return round(self.bet, 2)