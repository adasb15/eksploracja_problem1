import numpy as np
from collections import defaultdict
from RatingSystem import RatingSystem

class MySystem(RatingSystem):
    def __init__(self):
        super().__init__()
        
        # Obliczenie globalnej średniej
        all_ratings = [r for ratings in self.movie_ratings.values() for r in ratings]
        self.global_avg = np.mean(all_ratings) if all_ratings else 3.5
        
        # Mapowanie dla szybkiego wyszukiwania sąsiadów
        self.movie_to_user_ratings = defaultdict(list)
        for u_id, user_obj in self.users.items():
            for m_id, rat in user_obj.ratings.items():
                self.movie_to_user_ratings[m_id].append((u_id, rat))
        
        # Średnie ocen dla każdego użytkownika w systemie
        self.user_stats = {}
        for u_id, user_obj in self.users.items():
            u_ratings = list(user_obj.ratings.values())
            if u_ratings:
                self.user_stats[u_id] = {
                    'avg': np.mean(u_ratings),
                    'norm': np.linalg.norm(u_ratings)
                }

    def _get_cosine_similarity(self, ratings1, ratings2):
        common_movies = set(ratings1.keys()) & set(ratings2.keys())
        if not common_movies:
            return 0
        
        v1 = np.array([ratings1[m] for m in common_movies])
        v2 = np.array([ratings2[m] for m in common_movies])
        
        dot_product = np.dot(v1, v2)

        norm1 = np.linalg.norm(list(ratings1.values()))
        norm2 = np.linalg.norm(list(ratings2.values()))
        
        return dot_product / (norm1 * norm2) if (norm1 * norm2) > 0 else 0

    def rate(self, user, movie_id):
        # Normalizacja movie_id
        m_id = movie_id.id if hasattr(movie_id, 'id') else int(movie_id)
        
        # Pobieramy użytkowników, którzy ocenili ten film
        potential_neighbors = self.movie_to_user_ratings.get(m_id, [])
        if not potential_neighbors or not user.ratings:
            movie_ratings = self.movie_ratings.get(m_id, [])
            return np.mean(movie_ratings) if movie_ratings else self.global_avg

        # Obliczamy podobieństwa dla sąsiadów
        similarities = []
        user_ratings_dict = user.ratings
        
        for neighbor_id, neighbor_rating in potential_neighbors:
            neighbor_obj = self.users.get(neighbor_id)
            if neighbor_obj:
                sim = self._get_cosine_similarity(user_ratings_dict, neighbor_obj.ratings)
                if sim > 0:
                    similarities.append((sim, neighbor_rating))

        # Sortujemy po podobieństwie i bierzemy top K
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_k = similarities[:10]

        if not top_k:
            return self.global_avg

        # Obliczamy ważoną średnią
        weighted_sum = sum(sim * rat for sim, rat in top_k)
        sum_of_weights = sum(sim for sim, rat in top_k)
        prediction = weighted_sum / sum_of_weights
        
        # Zaokrąglamy do 0.5
        prediction = round(prediction * 2) / 2
        return max(0.5, min(5.0, float(prediction)))

    def __str__(self):
        """
        Ta metoda zwraca numery indeksów wszystkich twórców rozwiązania. Poniżej przykład.
        """
        return "System created by 155898 and 156021 and 155934"
