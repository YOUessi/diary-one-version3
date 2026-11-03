"""Integration regression: long-day thematic planning can call real media selector.

This test guards a late NameError that previously occurred after S09A used
44–47 successful real provider calls. It does not simulate image quality.
"""
from diary_one_ci import product_editor, chapter_episode_router, chapter_theme_hierarchy


def test_media_only_selector_is_imported_in_product_editor():
    assert product_editor.chapter_episode_router is chapter_episode_router
    assert callable(product_editor.chapter_episode_router.select_media)
    assert callable(chapter_theme_hierarchy.plan)
