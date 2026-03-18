import numpy as np
from RatingSystem import RatingSystem

class MySystem(RatingSystem):
    def __init__(self):
        super().__init__()
        
        all_ratings = [r for ratings in self.movie_ratings.values() for r in ratings]
        self.global_avg = np.mean(all_ratings) if all_ratings else 3
        self.movie_means = {}
        for m_id, ratings in self.movie_ratings.items():
            n = len(ratings)
            # Im więcej ocen, tym bardziej ufamy średniej filmu
            self.movie_means[m_id] = (sum(ratings) + 10 * self.global_avg) / (n + 10)

    def rate(self, user, movie):
        m_id = movie.id if hasattr(movie, 'id') else int(movie)
        movie_avg = self.movie_means.get(m_id, self.global_avg)
        
        # Obliczamy bias użytkownika
        user_ratings = list(user.ratings.values())
        if not user_ratings:
            return movie_avg
            
        u_n = len(user_ratings)
        user_avg = (sum(user_ratings) + 5 * self.global_avg) / (u_n + 5)
        raw_user_bias = user_avg - self.global_avg
        confidence_multiplier = 0.7 
        adjusted_user_bias = raw_user_bias * confidence_multiplier
        
        prediction = movie_avg + adjusted_user_bias
        prediction = round(prediction * 2) / 2
        
        return max(0.5, min(5.0, float(prediction)))

    def __str__(self):
        """
        Ta metoda zwraca numery indeksów wszystkich twórców rozwiązania. Poniżej przykład.
        """
        return "System created by 155898 and 156021 and 155934"
