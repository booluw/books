"""Tests for event-time windows, watermarks, late data and Chandy-Lamport."""

import unittest

from snapshot import naive_snapshot, run_snapshot
from windows import (Event, Sliding, Tumbling, WindowOperator, event_time_truth,
                     generate_events, mean_abs_error, processing_time_windows,
                     run_event_time)


def ev(event_time, arrival, eid=0):
    return Event(arrival, event_time, "all", 1.0, eid)


class AssignerTests(unittest.TestCase):
    def test_tumbling_assigns_exactly_one_window(self):
        self.assertEqual(Tumbling(10).assign(23.5), [(20, 30)])
        self.assertEqual(Tumbling(10).assign(30.0), [(30, 40)])   # windows are [start, end)

    def test_sliding_assigns_size_over_slide_windows(self):
        self.assertEqual(Sliding(10, 5).assign(12), [(5, 15), (10, 20)])
        self.assertEqual(len(Sliding(60, 10).assign(125.0)), 6)


class WatermarkTests(unittest.TestCase):
    def test_in_order_stream_matches_batch_truth(self):
        events = [ev(t * 0.5, t * 0.5, t) for t in range(100)]
        op = run_event_time(events, Tumbling(10), max_delay=0)
        self.assertEqual(op.final(), event_time_truth(events, Tumbling(10)))
        self.assertEqual(op.dropped, [])

    def test_disorder_within_bound_is_absorbed(self):
        # Each event arrives up to 3 s late; a 3 s watermark delay loses nothing.
        events = [ev(t, t + (3 if t % 4 == 0 else 0), t) for t in range(40)]
        op = run_event_time(events, Tumbling(10), max_delay=3)
        self.assertEqual(op.final(), event_time_truth(events, Tumbling(10)))

    def test_window_fires_only_when_watermark_passes_end(self):
        op = WindowOperator(Tumbling(10), max_delay=2)
        op.process(ev(5, 5))
        self.assertEqual(op.process(ev(11, 11)), [])       # watermark 9 < 10
        fired = op.process(ev(12, 12.1))                   # watermark 10 >= 10
        self.assertEqual([(r.window, r.count, r.emitted_at) for r in fired],
                         [((0, 10), 1, 12.1)])

    def test_late_event_dropped_or_sent_to_side_output(self):
        stream = [ev(1, 1), ev(15, 15), ev(2, 16)]         # the last is behind the watermark
        dropped = run_event_time(stream, Tumbling(10), max_delay=0)
        side = run_event_time(stream, Tumbling(10), max_delay=0, late_policy="side")
        self.assertEqual(len(dropped.dropped), 1)
        self.assertEqual([e.event_time for e in side.side_output], [2])
        self.assertEqual(side.final()[("all", (0, 10))], 1)

    def test_allowed_lateness_emits_update(self):
        stream = [ev(1, 1), ev(15, 15), ev(2, 16), ev(40, 40), ev(3, 41)]
        op = run_event_time(stream, Tumbling(10), max_delay=0, allowed_lateness=10)
        updates = [r for r in op.results if r.update]
        self.assertEqual([(r.window, r.count) for r in updates], [((0, 10), 2)])
        self.assertEqual(len(op.dropped), 1)               # t=3 arrived after 10 + 10 s

    def test_more_watermark_delay_trades_latency_for_completeness(self):
        events = generate_events(seed=2)
        lost = [len(run_event_time(events, Tumbling(10), max_delay=d).dropped)
                for d in (0, 2, 10, 60)]
        self.assertEqual(lost, sorted(lost, reverse=True))
        self.assertEqual(lost[-1], 0)

    def test_processing_time_windows_differ_from_event_time(self):
        events = generate_events(seed=1)
        truth = event_time_truth(events, Tumbling(10))
        proc = processing_time_windows(events, Tumbling(10))
        event = run_event_time(events, Tumbling(10), max_delay=5, allowed_lateness=60).final()
        self.assertEqual(event, truth)
        self.assertGreater(mean_abs_error(proc, truth), 20)
        self.assertLess(proc[("all", (40.0, 50.0))], truth[("all", (40.0, 50.0))] / 4)

    def test_generator_is_deterministic(self):
        self.assertEqual(generate_events(seed=9), generate_events(seed=9))


class SnapshotTests(unittest.TestCase):
    def test_snapshot_conserves_money_across_randomised_runs(self):
        for seed in range(300):
            bank, snap = run_snapshot(seed)
            self.assertEqual(snap.total, bank.invariant, f"seed {seed}")
            self.assertTrue(bank.is_consistent_cut(), f"seed {seed}")

    def test_channel_state_is_exactly_the_money_in_flight_at_the_cut(self):
        for seed in range(50):
            bank, snap = run_snapshot(seed, n=4)
            for (src, dst), amounts in snap.channels.items():
                expected = [bank.messages[m][2]
                            for m in sorted(bank.procs[src].sent_at_record)
                            if bank.messages[m][1] == dst
                            and m not in bank.procs[dst].received_at_record]
                self.assertEqual(amounts, expected, f"seed {seed} channel {src}->{dst}")

    def test_without_fifo_or_markers_snapshots_go_wrong(self):
        reorder_wrong = sum(run_snapshot(s, fifo=False)[1].total != 3_000 for s in range(100))
        naive_wrong = sum(naive_snapshot(s) != 3_000 for s in range(100))
        self.assertGreater(reorder_wrong, 50)
        self.assertGreater(naive_wrong, 50)


if __name__ == "__main__":
    unittest.main()
