import numpy as np
import csv
from tqdm import tqdm
from RatingSystem import RatingSystem


class MySystem(RatingSystem):

    def __init__(self):
        super().__init__()
        all_ratings = [r for ratings in self.movie_ratings.values() for r in ratings]
        self.global_avg = np.mean(all_ratings) if all_ratings else 2.5
        self.movie_means = {}
        for m_id, ratings in self.movie_ratings.items():
            self.movie_means[m_id] = np.mean(ratings) if ratings else self.global_avg

    def rate(self, user, movie):
        m_id = movie.id if hasattr(movie, 'id') else int(movie)
        user_ratings = list(user.ratings.values())
        user_avg = np.mean(user_ratings) if user_ratings else self.global_avg
        movie_avg = self.movie_means.get(m_id, self.global_avg)
        prediction = (user_avg + movie_avg) / 2
        return max(0.5, min(5.0, float(prediction)))

    def __str__(self):
        """
        Ta metoda zwraca numery indeksów wszystkich twórców rozwiązania. Poniżej przykład.
        """
        return "System created by 155898 and 156021 and 155934"
