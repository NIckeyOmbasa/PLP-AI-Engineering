class CryptoAdvisor:
    def __init__(self):
        self.name = "CryptoAdvisor"
        self.greeting = "🤖 Welcome to CryptoAdvisor! I'll help you find profitable AND sustainable crypto investments."
        self.disclaimer = "\n⚠️ Disclaimer: Crypto investments carry risk. This is not financial advice. Always do your own research!"
        
        # Predefined cryptocurrency database
        self.crypto_db = {  
            "Bitcoin": {  
                "price_trend": "rising",  
                "market_cap": "high",  
                "energy_use": "high",  
                "sustainability_score": 3/10,
                "risk": "high"
            },  
            "Ethereum": {  
                "price_trend": "stable",  
                "market_cap": "high",  
                "energy_use": "medium",  
                "sustainability_score": 6/10,
                "risk": "medium"
            },  
            "Cardano": {  
                "price_trend": "rising",  
                "market_cap": "medium",  
                "energy_use": "low",  
                "sustainability_score": 8/10,
                "risk": "medium"
            },
            "Solana": {
                "price_trend": "rising",
                "market_cap": "medium",
                "energy_use": "low",
                "sustainability_score": 7/10,
                "risk": "medium"
            },
            "Algorand": {
                "price_trend": "stable",
                "market_cap": "low",
                "energy_use": "very low",
                "sustainability_score": 9/10,
                "risk": "low"
            }
        }
    
    def start_chat(self):
        print(f"\n{self.greeting}")
        print("You can ask me about:")
        print("- Trending cryptocurrencies")
        print("- Sustainable/eco-friendly coins")
        print("- Best options for long-term growth")
        print("- Low risk investments")
        print("- Type 'quit' to exit\n")
        
        while True:
            user_query = input("You: ").lower()
            
            if user_query in ['quit', 'exit', 'bye']:
                print(f"{self.name}: Happy investing! Remember to diversify your portfolio.{self.disclaimer}")
                break
                
            self.respond_to_query(user_query)
    
    def respond_to_query(self, query):
        if not query:
            print(f"{self.name}: Could you please rephrase your question?")
            return
            
        # Check for different types of queries
        if any(word in query for word in ['trend', 'rising', 'upward', 'growing']):
            self.recommend_by_trend()
        elif any(word in query for word in ['sustainab', 'eco', 'green', 'environment']):
            self.recommend_by_sustainability()
        elif any(word in query for word in ['long term', 'long-term', 'future', 'growth']):
            self.recommend_long_term()
        elif any(word in query for word in ['risk', 'safe', 'low risk', 'secure']):
            self.recommend_low_risk()
        elif any(word in query for word in ['help', 'what can you do']):
            self.show_help()
        else:
            print(f"{self.name}: I'm not sure I understand. Try asking about trends, sustainability, or long-term potential.")
    
    def recommend_by_trend(self):
        trending = [coin for coin in self.crypto_db 
                   if self.crypto_db[coin]["price_trend"] == "rising"]
        
        if not trending:
            print(f"{self.name}: Currently no cryptocurrencies show strong upward trends.")
            return
            
        print(f"{self.name}: These cryptocurrencies are currently trending up:")
        for coin in trending:
            print(f"- {coin} (Market cap: {self.crypto_db[coin]['market_cap']}, Risk: {self.crypto_db[coin]['risk']})")
        
        top_pick = max(trending, key=lambda x: self.crypto_db[x]["market_cap"])
        print(f"\nMy top trending pick: {top_pick} (high market cap + rising price)")
        print(self.disclaimer)
    
    def recommend_by_sustainability(self):
        sustainable_coins = sorted(
            [(coin, data) for coin, data in self.crypto_db.items()],
            key=lambda x: -x[1]["sustainability_score"]
        )
        
        print(f"{self.name}: Most sustainable cryptocurrencies:")
        for coin, data in sustainable_coins[:3]:  # Show top 3
            print(f"- {coin} (Sustainability: {data['sustainability_score']*10}/10, Energy use: {data['energy_use']})")
        
        top_pick = sustainable_coins[0][0]
        print(f"\nMy top sustainability pick: {top_pick} (best sustainability score)")
        print(self.disclaimer)
    
    def recommend_long_term(self):
        # Balance between sustainability and market cap for long-term
        long_term_coins = sorted(
            [(coin, data) for coin, data in self.crypto_db.items()],
            key=lambda x: (-x[1]["sustainability_score"], -0.5 if x[1]["market_cap"] == "high" else 0)
        )
        
        print(f"{self.name}: Best options for long-term growth (sustainability + market cap):")
        for coin, data in long_term_coins[:3]:
            print(f"- {coin} (Sustainability: {data['sustainability_score']*10}/10, Market cap: {data['market_cap']})")
        
        top_pick = long_term_coins[0][0]
        print(f"\nMy long-term pick: {top_pick} (good balance of sustainability and market presence)")
        print(self.disclaimer)
    
    def recommend_low_risk(self):
        low_risk_coins = [coin for coin in self.crypto_db 
                         if self.crypto_db[coin]["risk"] == "low"]
        
        if not low_risk_coins:
            print(f"{self.name}: Currently no low-risk cryptocurrencies available. Consider stablecoins instead.")
            return
            
        print(f"{self.name}: Lower risk cryptocurrency options:")
        for coin in low_risk_coins:
            data = self.crypto_db[coin]
            print(f"- {coin} (Risk: {data['risk']}, Market cap: {data['market_cap']})")
        
        print(self.disclaimer)
    
    def show_help(self):
        print(f"{self.name}: I can help with:")
        print("- 'Which cryptocurrencies are trending up?'")
        print("- 'What are the most sustainable coins?'")
        print("- 'What's good for long-term investment?'")
        print("- 'Show me low-risk crypto options'")
        print("- 'quit' to exit")

# Start the chatbot
if __name__ == "__main__":
    bot = CryptoAdvisor()
    bot.start_chat()
