from abc import ABC, abstractmethod

class TestAbstractClass(ABC):
    @abstractmethod
    def sum_wallet():
        pass

    @abstractmethod
    def financial_data():
        pass

    @abstractmethod
    def update_exchange_rates(n):
        pass

    @abstractmethod
    def change_control_finance(f):
        pass

    @abstractmethod
    async def get_amount(request):
        pass

    @abstractmethod
    async def get_rub(request):
        pass

    @abstractmethod
    async def get_usd(request):
        pass

    @abstractmethod
    async def get_eur(request):
        pass

    @abstractmethod
    async def post_wallet(request):
        pass

    @abstractmethod
    async def post_change_wallet(request):
        pass