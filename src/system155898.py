import numpy as np
import heapq
from collections import defaultdict
from RatingSystem import RatingSystem, test_pairs

class MySystem(RatingSystem):
    def __init__(self):
        super().__init__()
        self.test_pairs_set = {(int(u), int(m)) for u, m in test_pairs}

        self.k_neighbors = 10

        # Obliczenie globalnej średniej i średnich ocen filmów
        ratings_sum = 0.0
        ratings_count = 0
        self.movie_means = {}
        for movie_id, ratings in self.movie_ratings.items():
            if ratings:
                movie_sum = float(sum(ratings))
                movie_count = len(ratings)
                self.movie_means[movie_id] = movie_sum / movie_count
                ratings_sum += movie_sum
                ratings_count += movie_count
        self.global_avg = (ratings_sum / ratings_count) if ratings_count else 3.5
        
        # Mapowanie dla szybkiego wyszukiwania sąsiadów
        self.movie_to_user_ratings = defaultdict(list)
        for u_id, user_obj in self.users.items():
            for m_id, rat in user_obj.ratings.items():
                if (int(u_id), int(m_id)) in self.test_pairs_set:
                    continue
                self.movie_to_user_ratings[m_id].append((u_id, rat))


        leaks = 0
        for user_id, movie_id in test_pairs:
            uid = int(user_id)
            mid = int(movie_id)
            if any(n_uid == uid for n_uid, _ in self.movie_to_user_ratings.get(mid, [])):
                leaks += 1

        print("Liczba test_pairs obecnych w movie_to_user_ratings:", leaks)


        # Normy ocen użytkowników liczone raz na starcie
        self.user_norms = {}
        for u_id, user_obj in self.users.items():
            u_ratings = list(user_obj.ratings.values())
            if u_ratings:
                self.user_norms[u_id] = float(np.linalg.norm(u_ratings))
            else:
                self.user_norms[u_id] = 0.0

    def _get_cosine_similarity(self, ratings1, ratings2, norm1, norm2):
        if norm1 <= 0.0 or norm2 <= 0.0:
            return 0

        # Liczymy iloczyn skalarny tylko na wspólnych filmach
        if len(ratings1) > len(ratings2):
            ratings1, ratings2 = ratings2, ratings1

        dot_product = 0.0
        has_common = False
        for movie_id, rating in ratings1.items():
            other = ratings2.get(movie_id)
            if other is not None:
                dot_product += rating * other
                has_common = True

        if not has_common:
            return 0

        return dot_product / (norm1 * norm2)

    def rate(self, user, movie_id):
        # Normalizacja movie_id
        m_id = movie_id.id if hasattr(movie_id, 'id') else int(movie_id)
        
        # Pobieramy użytkowników, którzy ocenili ten film
        potential_neighbors = self.movie_to_user_ratings.get(m_id, [])
        if not potential_neighbors or not user.ratings:
            return self.movie_means.get(m_id, self.global_avg)

        # Obliczamy podobieństwa dla sąsiadów
        similarities = []
        user_ratings_dict = user.ratings
        user_norm = float(np.linalg.norm(list(user_ratings_dict.values())))
        if user_norm <= 0.0:
            return self.movie_means.get(m_id, self.global_avg)
        
        for neighbor_id, neighbor_rating in potential_neighbors:
            neighbor_obj = self.users.get(neighbor_id)
            if neighbor_obj:
                neighbor_norm = self.user_norms.get(neighbor_id, 0.0)
                sim = self._get_cosine_similarity(
                    user_ratings_dict, neighbor_obj.ratings, user_norm, neighbor_norm
                )
                if sim > 0:
                    similarities.append((sim, neighbor_rating))

        # Bierzemy top K najbardziej podobnych użytkowników
        top_k = heapq.nlargest(self.k_neighbors, similarities, key=lambda x: x[0])

        if not top_k:
            return self.movie_means.get(m_id, self.global_avg)

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
