import csv
from collections import defaultdict

from RatingSystem import RatingSystem


class MySystem(RatingSystem):
    def __init__(self):
        super().__init__()
        self.default_global = 2.5
        self.movie_reg = 10.0
        self.user_reg = 5.0
        self.genre_reg = 5.0
        self.user_bias_weight = 0.7
        self.user_genre_weight = 0.5
        self.global_genre_weight = 0.2
        self.user_conf_reg = 10.0
        self.genre_conf_reg = 8.0

        all_ratings = [r for ratings in self.movie_ratings.values() for r in ratings]
        self.global_avg = sum(all_ratings) / len(all_ratings) if all_ratings else self.default_global
        self.movie_genres = self._load_movie_genres()
        self.movie_means = {}
        for movie_id, ratings in self.movie_ratings.items():
            n = len(ratings)
            self.movie_means[movie_id] = (sum(ratings) + self.movie_reg * self.global_avg) / (n + self.movie_reg)
        self.genre_sum = defaultdict(float)
        self.genre_count = defaultdict(int)
        for movie_id, ratings in self.movie_ratings.items():
            genres = self.movie_genres.get(movie_id, set())
            for rating in ratings:
                for genre in genres:
                    self.genre_sum[genre] += rating
                    self.genre_count[genre] += 1
        self.user_genre_sum = defaultdict(lambda: defaultdict(float))
        self.user_genre_count = defaultdict(lambda: defaultdict(int))
        for user_id, user_obj in self.users.items():
            for rated_movie_id, rating in user_obj.ratings.items():
                for genre in self.movie_genres.get(rated_movie_id, set()):
                    self.user_genre_sum[user_id][genre] += rating
                    self.user_genre_count[user_id][genre] += 1

    def _load_movie_genres(self):
        result = {}
        with open("./data/movie.csv", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                genres = set()
                if len(row) > 2 and row[2]:
                    genres = {g for g in row[2].split("|") if g and g != "(no genres listed)"}
                result[int(row[0])] = genres
        return result

    def rate(self, user, movie):
        movie_id = movie.id if hasattr(movie, "id") else int(movie)
        movie_avg = self.movie_means.get(movie_id, self.global_avg)

        user_ratings = list(user.ratings.values())
        if not user_ratings:
            pred = movie_avg
        else:
            n_user = len(user_ratings)
            user_avg = (sum(user_ratings) + self.user_reg * self.global_avg) / (n_user + self.user_reg)
            user_conf = n_user / (n_user + self.user_conf_reg)
            user_bias = (user_avg - self.global_avg) * self.user_bias_weight * user_conf
            target_genres = self.movie_genres.get(movie_id, set())
            user_id = getattr(user, "id", None)
            user_genre_scores = self.user_genre_sum.get(user_id, {})
            user_genre_counts = self.user_genre_count.get(user_id, {})
            rated_target = user.ratings.get(movie_id)
            target_movie_genres = self.movie_genres.get(movie_id, set())

            user_genre_biases = []
            global_genre_biases = []
            genre_counts_local = []
            for genre in target_genres:
                ug_sum = user_genre_scores.get(genre, 0.0)
                ug_count = user_genre_counts.get(genre, 0)
                if rated_target is not None and genre in target_movie_genres and ug_count > 0:
                    ug_sum -= rated_target
                    ug_count -= 1
                ug_avg = (ug_sum + self.genre_reg * self.global_avg) / (ug_count + self.genre_reg)
                gg_avg = (self.genre_sum[genre] + self.genre_reg * self.global_avg) / (self.genre_count[genre] + self.genre_reg)
                user_genre_biases.append(ug_avg - self.global_avg)
                global_genre_biases.append(gg_avg - self.global_avg)
                genre_counts_local.append(ug_count)

            user_genre_bias = (sum(user_genre_biases) / len(user_genre_biases) if user_genre_biases else 0.0)
            global_genre_bias = (sum(global_genre_biases) / len(global_genre_biases) if global_genre_biases else 0.0)
            avg_genre_count = (sum(genre_counts_local) / len(genre_counts_local)) if genre_counts_local else 0.0
            genre_conf = avg_genre_count / (avg_genre_count + self.genre_conf_reg)
            pred = movie_avg + user_bias + genre_conf * (
                self.user_genre_weight * user_genre_bias + self.global_genre_weight * global_genre_bias
            )
            
        pred = round(pred * 2) / 2
        return max(0.5, min(5.0, float(pred)))

    def __str__(self):
        """
        Ta metoda zwraca numery indeksów wszystkich twórców rozwiązania. Poniżej przykład.
        """
        return "System created by 155898 and 156021 and 155934"
