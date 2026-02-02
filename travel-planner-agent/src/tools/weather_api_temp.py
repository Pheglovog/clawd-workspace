        # 生成建议
        advice = {
            "weather": weather,
            "forecast": forecast,
            "tips": self._generate_tips(weather, forecast),
            "clothing": self._generate_clothing_advice(weather, forecast),
            "best_days": self._find_best_days(forecast)
        }

        return advice