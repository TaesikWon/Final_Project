import requests
import xmltodict

API_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"


class RealPriceAPI:
    def __init__(self, service_key: str):
        self.service_key = service_key

    def fetch(self, region_code: str, deal_ym: str):
        """region_code: '41110', deal_ym: '202501' 형식"""
        params = {
            "serviceKey": self.service_key,
            "LAWD_CD": region_code,
            "DEAL_YMD": deal_ym,
        }
        res = requests.get(API_URL, params=params)
        data = xmltodict.parse(res.text)

        try:
            items = data["response"]["body"]["items"]["item"]
        except:
            return []

        if isinstance(items, dict):
            return [items]

        return items

    def recent_3m(self, region_code: str, apt_name: str):
        """최근 3개월 아파트 평균가"""
        from datetime import datetime, timedelta

        now = datetime.now()
        months = [(now.replace(day=1) - timedelta(days=30 * i)).strftime("%Y%m") for i in range(3)]

        prices = []

        for ym in months:
            items = self.fetch(region_code, ym)
            for it in items:
                if apt_name in it.get("아파트", ""):
                    price = it.get("거래금액")
                    if price:
                        prices.append(int(price.replace(",", "")))

        if not prices:
            return 0
        return sum(prices) / len(prices)
