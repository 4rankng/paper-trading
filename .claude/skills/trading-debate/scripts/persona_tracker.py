#!/usr/bin/env python3
"""
Persona Tracker - Historical accuracy tracking for debate personas.

Tracks:
- Challenge success/failure rates
- Concession rates
- Vote correctness (when outcomes known)
- Historical accuracy scores

Uses SQLite for persistence.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PersonaTracker:
    """Tracks persona performance across debates for confidence weighting."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize tracker with database path."""
        if db_path is None:
            # Default to skill data directory
            skill_dir = Path(__file__).parent.parent
            data_dir = skill_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "debate_history.db"

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Persona accuracy table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persona_accuracy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_name TEXT UNIQUE,
                debates_participated INTEGER DEFAULT 0,
                successful_challenges INTEGER DEFAULT 0,
                failed_challenges INTEGER DEFAULT 0,
                concessions_made INTEGER DEFAULT 0,
                votes_correct INTEGER DEFAULT 0,
                votes_total INTEGER DEFAULT 0,
                accuracy_score REAL DEFAULT 0.5,
                last_updated TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Debate outcomes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debate_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                timeframe TEXT,
                model TEXT,
                mode TEXT,
                date TEXT,
                verdict TEXT,
                conviction TEXT,
                personas_participated TEXT,
                challenges_issued INTEGER DEFAULT 0,
                challenges_successful INTEGER DEFAULT 0,
                rounds_completed INTEGER DEFAULT 0,
                final_confidence REAL,
                actual_outcome TEXT DEFAULT 'PENDING',
                outcome_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER,
                round_number INTEGER,
                challenger_persona TEXT,
                target_persona TEXT,
                challenge_summary TEXT,
                response_summary TEXT,
                was_successful BOOLEAN,
                concession BOOLEAN,
                quality_score REAL DEFAULT 0.5,
                FOREIGN KEY (debate_id) REFERENCES debate_outcomes(id)
            )
        """)

        # Vote tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persona_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER,
                persona_name TEXT,
                vote TEXT,
                weight REAL,
                was_correct BOOLEAN,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debate_id) REFERENCES debate_outcomes(id)
            )
        """)

        conn.commit()
        conn.close()

    def register_debate(self, ticker: str, timeframe: str, model: str,
                        mode: str, personas: List[str]) -> int:
        """Register a new debate and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO debate_outcomes
            (ticker, timeframe, model, mode, date, personas_participated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, timeframe, model, mode,
              datetime.now().isoformat(), json.dumps(personas)))

        debate_id = cursor.lastrowid

        # Update participation counts
        for persona in personas:
            cursor.execute("""
                INSERT OR IGNORE INTO persona_accuracy (persona_name, last_updated)
                VALUES (?, ?)
            """, (persona, datetime.now().isoformat()))

            cursor.execute("""
                UPDATE persona_accuracy
                SET debates_participated = debates_participated + 1,
                    last_updated = ?
                WHERE persona_name = ?
            """, (datetime.now().isoformat(), persona))

        conn.commit()
        conn.close()

        return debate_id

    def record_challenge(self, debate_id: int, round_number: int,
                         challenger: str, target: str,
                         challenge_summary: str, response_summary: str,
                         was_successful: bool, concession: bool,
                         quality_score: float = 0.5):
        """Record a challenge and its outcome."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO challenges
            (debate_id, round_number, challenger_persona, target_persona,
             challenge_summary, response_summary, was_successful, concession, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (debate_id, round_number, challenger, target,
              challenge_summary, response_summary,
              was_successful, concession, quality_score))

        # Update challenger stats
        cursor.execute("""
            INSERT OR IGNORE INTO persona_accuracy (persona_name, last_updated)
            VALUES (?, ?)
        """, (challenger, datetime.now().isoformat()))

        if was_successful:
            cursor.execute("""
                UPDATE persona_accuracy
                SET successful_challenges = successful_challenges + 1,
                    last_updated = ?
                WHERE persona_name = ?
            """, (datetime.now().isoformat(), challenger))
        else:
            cursor.execute("""
                UPDATE persona_accuracy
                SET failed_challenges = failed_challenges + 1,
                    last_updated = ?
                WHERE persona_name = ?
            """, (datetime.now().isoformat(), challenger))

        # Update target stats (concessions)
        if concession:
            cursor.execute("""
                UPDATE persona_accuracy
                SET concessions_made = concessions_made + 1,
                    last_updated = ?
                WHERE persona_name = ?
            """, (datetime.now().isoformat(), target))

        conn.commit()
        conn.close()

    def record_votes(self, debate_id: int, votes: Dict[str, str],
                     weights: Dict[str, float]):
        """Record votes from all personas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for persona, vote in votes.items():
            weight = weights.get(persona, 0.5)
            cursor.execute("""
                INSERT INTO persona_votes
                (debate_id, persona_name, vote, weight)
                VALUES (?, ?, ?, ?)
            """, (debate_id, persona, vote, weight))

        conn.commit()
        conn.close()

    def finalize_debate(self, debate_id: int, verdict: str, conviction: str,
                        rounds_completed: int, final_confidence: float,
                        challenges_issued: int, challenges_successful: int):
        """Finalize a debate with its outcome."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE debate_outcomes
            SET verdict = ?, conviction = ?, rounds_completed = ?,
                final_confidence = ?, challenges_issued = ?,
                challenges_successful = ?
            WHERE id = ?
        """, (verdict, conviction, rounds_completed, final_confidence,
              challenges_issued, challenges_successful, debate_id))

        conn.commit()
        conn.close()

        # Recalculate accuracy scores
        self._recalculate_accuracy()

    def record_outcome(self, debate_id: int, actual_outcome: str,
                       notes: str = ""):
        """Record the actual outcome of a debate (later, when known)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE debate_outcomes
            SET actual_outcome = ?, outcome_date = ?, notes = ?
            WHERE id = ?
        """, (actual_outcome, datetime.now().isoformat(), notes, debate_id))

        # Update persona correctness based on their votes
        cursor.execute("""
            SELECT pv.id, pv.persona_name, pv.vote, do.verdict
            FROM persona_votes pv
            JOIN debate_outcomes do ON do.id = pv.debate_id
            WHERE pv.debate_id = ? AND pv.was_correct IS NULL
        """, (debate_id,))

        rows = cursor.fetchall()

        for row in rows:
            vote_id, persona, vote, verdict = row
            # Correct if vote aligned with verdict (or both neutral)
            was_correct = (vote == verdict or
                          vote in ["WATCH", "HOLD"] and verdict in ["WATCH", "HOLD"])

            cursor.execute("""
                UPDATE persona_votes
                SET was_correct = ?
                WHERE id = ?
            """, (was_correct, vote_id))

            # Update persona accuracy stats
            cursor.execute("""
                UPDATE persona_accuracy
                SET votes_total = votes_total + 1
                WHERE persona_name = ?
            """, (persona,))

            if was_correct:
                cursor.execute("""
                    UPDATE persona_accuracy
                    SET votes_correct = votes_correct + 1
                    WHERE persona_name = ?
                """, (persona,))

        conn.commit()
        conn.close()

        # Recalculate accuracy scores
        self._recalculate_accuracy()

    def _recalculate_accuracy(self):
        """Recalculate accuracy scores for all personas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT persona_name FROM persona_accuracy")
        personas = [row[0] for row in cursor.fetchall()]

        for persona in personas:
            # Calculate challenge success rate
            cursor.execute("""
                SELECT successful_challenges, failed_challenges
                FROM persona_accuracy
                WHERE persona_name = ?
            """, (persona,))

            successful, failed = cursor.fetchone()
            total_challenges = successful + failed

            challenge_success = (
                successful / total_challenges if total_challenges > 0 else 0.5
            )

            # Calculate vote correctness
            cursor.execute("""
                SELECT votes_correct, votes_total
                FROM persona_accuracy
                WHERE persona_name = ?
            """, (persona,))

            correct, total = cursor.fetchone()
            vote_accuracy = correct / total if total > 0 else 0.5

            # Combined accuracy score (70% challenge success, 30% vote accuracy)
            accuracy = (challenge_success * 0.7) + (vote_accuracy * 0.3)

            cursor.execute("""
                UPDATE persona_accuracy
                SET accuracy_score = ?
                WHERE persona_name = ?
            """, (accuracy, persona))

        conn.commit()
        conn.close()

    def get_persona_weight(self, persona: str,
                           min_debates: int = 10) -> float:
        """Get voting weight for a persona based on historical accuracy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT accuracy_score, debates_participated
            FROM persona_accuracy
            WHERE persona_name = ?
        """, (persona,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return 0.5  # Default weight for new persona

        accuracy, debates = row

        if debates < min_debates:
            return 0.5  # Default weight until minimum debates reached

        # Weight = 0.5 + (accuracy - 0.5) * influence_factor
        # This keeps weights in [0, 1] range centered at 0.5
        return max(0.1, min(1.0, 0.5 + (accuracy - 0.5)))

    def get_all_weights(self, personas: List[str],
                        min_debates: int = 10) -> Dict[str, float]:
        """Get voting weights for all personas."""
        return {p: self.get_persona_weight(p, min_debates) for p in personas}

    def get_challenge_success_rate(self, persona: str,
                                   min_challenges: int = 3) -> Tuple[float, int]:
        """Get challenge success rate and total challenges for a persona."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT successful_challenges, failed_challenges
            FROM persona_accuracy
            WHERE persona_name = ?
        """, (persona,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return 0.5, 0

        successful, failed = row
        total = successful + failed

        if total < min_challenges:
            return 1.0, total  # No penalty until minimum challenges

        return successful / total if total > 0 else 0.5, total

    def should_mute_persona(self, persona: str, mute_threshold: float = 0.30,
                            min_challenges: int = 3) -> bool:
        """Check if a persona should be muted due to low challenge success."""
        success_rate, total = self.get_challenge_success_rate(persona, min_challenges)

        if total < min_challenges:
            return False

        return success_rate < mute_threshold

    def get_persona_stats(self, persona: str) -> Dict:
        """Get full stats for a persona."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM persona_accuracy WHERE persona_name = ?
        """, (persona,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return {
                "persona_name": persona,
                "debates_participated": 0,
                "successful_challenges": 0,
                "failed_challenges": 0,
                "concessions_made": 0,
                "votes_correct": 0,
                "votes_total": 0,
                "accuracy_score": 0.5
            }

        columns = ["id", "persona_name", "debates_participated",
                   "successful_challenges", "failed_challenges",
                   "concessions_made", "votes_correct", "votes_total",
                   "accuracy_score", "last_updated", "created_at"]

        return dict(zip(columns, row))

    def get_all_stats(self) -> List[Dict]:
        """Get stats for all personas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM persona_accuracy ORDER BY accuracy_score DESC")
        rows = cursor.fetchall()
        conn.close()

        columns = ["id", "persona_name", "debates_participated",
                   "successful_challenges", "failed_challenges",
                   "concessions_made", "votes_correct", "votes_total",
                   "accuracy_score", "last_updated", "created_at"]

        return [dict(zip(columns, row)) for row in rows]

    def get_persona_score(self, persona: str) -> float:
        """Calculate persona score: (successful_challenges × 2) - (concessions × 1) - (failed × 0.5)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT successful_challenges, failed_challenges, concessions_made
            FROM persona_accuracy
            WHERE persona_name = ?
        """, (persona,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return 0.0

        successful, failed, concessions = row

        score = (successful * 2) - (concessions * 1) - (failed * 0.5)
        return score


def main():
    """CLI for persona tracker operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage persona tracking data")
    parser.add_argument("--stats", action="store_true", help="Show all persona stats")
    parser.add_argument("--persona", help="Show stats for specific persona")
    parser.add_argument("--weights", nargs="+", help="Get weights for personas")
    parser.add_argument("--db", help="Path to database file")

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    tracker = PersonaTracker(db_path)

    if args.stats:
        stats = tracker.get_all_stats()
        print("\n=== Persona Stats ===\n")
        for s in stats:
            print(f"{s['persona_name']}:")
            print(f"  Debates: {s['debates_participated']}")
            print(f"  Challenges: {s['successful_challenges']}/{s['successful_challenges'] + s['failed_challenges']} successful")
            print(f"  Concessions: {s['concessions_made']}")
            print(f"  Accuracy: {s['accuracy_score']:.2%}")
            print(f"  Score: {tracker.get_persona_score(s['persona_name']):.1f}")
            print()

    elif args.persona:
        stats = tracker.get_persona_stats(args.persona)
        print(f"\n=== {args.persona} Stats ===\n")
        for k, v in stats.items():
            if k not in ["id", "created_at", "last_updated"]:
                print(f"  {k}: {v}")

    elif args.weights:
        weights = tracker.get_all_weights(args.weights)
        print("\n=== Persona Weights ===\n")
        for persona, weight in sorted(weights.items(), key=lambda x: -x[1]):
            print(f"  {persona}: {weight:.2f}")


if __name__ == "__main__":
    main()
