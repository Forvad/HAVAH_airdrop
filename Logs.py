class SaveAddres:
    @staticmethod
    def logs(text: str) -> None:
        with open('Wallet.txt', 'a', encoding="utf-8") as f:
            f.write(f'{str(text)}\n')

    @staticmethod
    def open_wallet():
        with open('Addres.txt', 'r', encoding="utf-8") as file:
            return file.read().splitlines()


