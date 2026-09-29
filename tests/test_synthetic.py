import numpy as np

from focuslens.synthetic import FEATURES, generate_training_data


def test_synthetic_generation_is_deterministic() -> None:
    first_features, first_labels = generate_training_data(samples=200, seed=7)
    second_features, second_labels = generate_training_data(samples=200, seed=7)

    assert first_features.shape == (200, len(FEATURES))
    assert np.array_equal(first_features, second_features)
    assert np.array_equal(first_labels, second_labels)
    assert set(first_labels).issubset({"focused", "neutral", "distracted"})
