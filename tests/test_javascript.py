# -*- coding: utf-8 -*-

# Any copyright is dedicated to the Public Domain.
# http://creativecommons.org/publicdomain/zero/1.0/

from pathlib import Path

from glean_parser import javascript
from glean_parser import metrics
from glean_parser import pings
from glean_parser import translate


ROOT = Path(__file__).parent


def test_parser(tmpdir):
    """Test translating metrics to Javascript files."""
    tmpdir = Path(str(tmpdir))

    translate.translate(
        ROOT / "data" / "core.yaml",
        "javascript",
        tmpdir,
        None,
        {"allow_reserved": True},
    )

    assert set(x.name for x in tmpdir.iterdir()) == set(
        [
            "corePing.js",
            "telemetry.js",
            "environment.js",
            "dottedCategory.js",
            "gleanInternalMetrics.js",
        ]
    )

    # Make sure descriptions made it in
    with (tmpdir / "corePing.js").open("r", encoding="utf-8") as fd:
        content = fd.read()
        assert "True if the user has set Firefox as the default browser." in content

    with (tmpdir / "telemetry.js").open("r", encoding="utf-8") as fd:
        content = fd.read()
        assert "جمع 搜集" in content

    with (tmpdir / "gleanInternalMetrics.js").open("r", encoding="utf-8") as fd:
        content = fd.read()
        assert 'category: ""' in content


def test_ping_parser(tmpdir):
    """Test translating pings to Javascript files."""
    tmpdir = Path(str(tmpdir))

    translate.translate(
        ROOT / "data" / "pings.yaml",
        "javascript",
        tmpdir,
        None,
        {"allow_reserved": True},
    )

    assert set(x.name for x in tmpdir.iterdir()) == set(["pings.js"])

    # Make sure descriptions made it in
    with (tmpdir / "pings.js").open("r", encoding="utf-8") as fd:
        content = fd.read()
        assert "This is a custom ping" in content


def test_javascript_generator():
    jdf = javascript.javascript_datatypes_filter
    assert jdf(metrics.Lifetime.ping) == '"ping"'


def test_metric_class_name():
    event = metrics.Event(
        type="event",
        category="category",
        name="metric",
        bugs=["http://bugzilla.mozilla.com/12345"],
        notification_emails=["nobody@example.com"],
        description="description...",
        expires="never",
        extra_keys={"my_extra": {"description": "an extra"}},
    )

    assert javascript.class_name(event.type) == "Glean._private.EventMetricType"

    boolean = metrics.Boolean(
        type="boolean",
        category="category",
        name="metric",
        bugs=["http://bugzilla.mozilla.com/12345"],
        notification_emails=["nobody@example.com"],
        description="description...",
        expires="never",
    )
    assert javascript.class_name(boolean.type) == "Glean._private.BooleanMetricType"

    ping = pings.Ping(
        name="custom",
        description="description...",
        include_client_id=True,
        bugs=["http://bugzilla.mozilla.com/12345"],
        notification_emails=["nobody@nowhere.com"],
    )
    assert javascript.class_name(ping.type) == "Glean._private.PingType"


# TODO: Activate once Glean.js adds support for labeled metric types in Bug 1682573.
#
# def test_duplicate(tmpdir):
#     """
#     Test that there aren't duplicate imports when using a labeled and
#     non-labeled version of the same metric.

#     https://github.com/mozilla-mobile/android-components/issues/2793
#     """

#     tmpdir = Path(str(tmpdir))

#     translate.translate(
#         ROOT / "data" / "duplicate_labeled.yaml",
#         "kotlin",
#         tmpdir,
#         {"namespace": "Foo"}
#     )

#     assert set(x.name for x in tmpdir.iterdir()) == set(["Category.kt"])

#     with (tmpdir / "Category.kt").open("r", encoding="utf-8") as fd:
#         content = fd.read()
#         assert (
#             content.count(
#                 "import mozilla.components.service.glean.private.CounterMetricType"
#             )
#             == 1
#         )

# TODO: Activate once Glean.js adds support for labeled metric types in Bug 1682573.
#
# def test_event_extra_keys_in_correct_order(tmpdir):
#     """
#     Assert that the extra keys appear in the parameter and the enumeration in
#     the same order.

#     https://bugzilla.mozilla.org/show_bug.cgi?id=1648768
#     """

#     tmpdir = Path(str(tmpdir))

#     translate.translate(
#         ROOT / "data" / "event_key_ordering.yaml",
#         "kotlin",
#         tmpdir,
#         {"namespace": "Foo"},
#     )

#     assert set(x.name for x in tmpdir.iterdir()) == set(["Event.kt"])

#     with (tmpdir / "Event.kt").open("r", encoding="utf-8") as fd:
#         content = fd.read()
#         content = " ".join(content.split())
#         assert "exampleKeys { alice, bob, charlie }" in content
#         assert 'allowedExtraKeys = listOf("alice", "bob", "charlie")' in content


def test_arguments_are_generated_in_deterministic_order(tmpdir):
    """
    Assert that arguments on generated code are always in the same order.

    https://bugzilla.mozilla.org/show_bug.cgi?id=1666192
    """

    tmpdir = Path(str(tmpdir))

    translate.translate(
        ROOT / "data" / "event_key_ordering.yaml",
        "javascript",
        tmpdir,
        None,
    )

    assert set(x.name for x in tmpdir.iterdir()) == set(["event.js"])

    with (tmpdir / "event.js").open("r", encoding="utf-8") as fd:
        content = fd.read()
        content = " ".join(content.split())
        expected = 'new Glean._private.EventMetricType({ category: "event", name: "example", sendInPings: ["events"], lifetime: "ping", disabled: false, }, ["alice", "bob", "charlie"]),'  # noqa
        assert expected in content
