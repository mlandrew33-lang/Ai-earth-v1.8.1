"""AI Earth v0.8 Education, Training, Qualification and Mastery Engine.

This module models learning and competency inside the simulation. It deliberately
uses an internal standards registry: simulated completion is not a claim of an
external legal qualification. Country standards can be loaded/updated from
trusted authoritative data in a future connector.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Competency:
    id: str
    title: str
    domain: str
    level: int
    outcomes: List[str]
    practical_evidence: List[str]


@dataclass(frozen=True)
class QualificationPath:
    id: str
    country: str
    framework: str
    title: str
    level: int
    competency_ids: List[str]


@dataclass
class TrainingRecord:
    competency_id: str
    score: float = 0.0
    practical_score: float = 0.0
    attempts: int = 0
    completed: bool = False
    verified: bool = False


@dataclass
class StandardsRegistry:
    competencies: Dict[str, Competency] = field(default_factory=dict)
    qualifications: Dict[str, QualificationPath] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "StandardsRegistry":
        r = cls()
        defaults = [
            Competency("CORE-DIGITAL", "Digital Literacy", "Core", 2,
                       ["Use digital tools safely", "Manage files and information"],
                       ["Complete a digital workflow independently"]),
            Competency("CORE-CODE", "Programming Fundamentals", "Coding", 3,
                       ["Use variables, conditions and functions", "Debug a small program"],
                       ["Build and test a working application"]),
            Competency("SOFT-SW", "Software Development", "Software", 4,
                       ["Design maintainable software", "Use tests and version control"],
                       ["Deliver a tested software project"]),
            Competency("GAME-DEV", "Game Development", "Creative Technology", 4,
                       ["Design game mechanics", "Implement a playable prototype"],
                       ["Ship a playable game prototype"]),
            Competency("CYBER-DEF", "Cybersecurity Defence", "Cybersecurity", 4,
                       ["Identify common threats", "Apply defensive controls"],
                       ["Investigate a simulated security incident"]),
            Competency("QC-INSPECT", "Quality Control Inspection", "Quality", 4,
                       ["Apply inspection criteria", "Record non-conformances"],
                       ["Complete and defend an inspection report"]),
            Competency("TRAIN-FAC", "Training Facilitation", "Education", 4,
                       ["Plan learning activities", "Facilitate and assess learners"],
                       ["Deliver a lesson and assess evidence"]),
            Competency("MEDIA-PROD", "Digital Media Production", "Media", 3,
                       ["Plan short-form content", "Edit and publish media"],
                       ["Produce a complete short video"]),
            Competency("BUS-ENT", "Entrepreneurship", "Business", 3,
                       ["Evaluate a market opportunity", "Build a basic business case"],
                       ["Present a viable product/service proposal"]),
        ]
        for c in defaults:
            r.competencies[c.id] = c
        r.qualifications["ZA-DIGITAL-3"] = QualificationPath(
            "ZA-DIGITAL-3", "South Africa", "NQF/SAQA-aligned registry",
            "Digital & Coding Foundation (simulation)", 3,
            ["CORE-DIGITAL", "CORE-CODE"])
        r.qualifications["GLOBAL-CODER-4"] = QualificationPath(
            "GLOBAL-CODER-4", "International", "AI Earth competency framework",
            "Software & Game Development Specialist (simulation)", 4,
            ["CORE-CODE", "SOFT-SW", "GAME-DEV"])
        r.qualifications["GLOBAL-CYBER-4"] = QualificationPath(
            "GLOBAL-CYBER-4", "International", "AI Earth competency framework",
            "Cybersecurity Defence Specialist (simulation)", 4,
            ["CORE-CODE", "CYBER-DEF"])
        r.qualifications["GLOBAL-QC-4"] = QualificationPath(
            "GLOBAL-QC-4", "International", "AI Earth competency framework",
            "Quality Control Inspector (simulation)", 4,
            ["QC-INSPECT", "CORE-DIGITAL"])
        return r


class EducationEngine:
    MASTERY = ("novice", "foundational", "competent", "proficient", "advanced", "expert", "master", "master_trainer", "researcher_innovator")

    def __init__(self, registry: StandardsRegistry | None = None):
        self.registry = registry or StandardsRegistry.default()

    def ensure_citizen(self, citizen):
        if not hasattr(citizen, "intelligence_capability"):
            citizen.intelligence_capability = 228
        if not hasattr(citizen, "knowledge_score"):
            citizen.knowledge_score = 20.0
        if not hasattr(citizen, "experience_score"):
            citizen.experience_score = 0.0
        if not hasattr(citizen, "mastery_scores"):
            citizen.mastery_scores = {}
        if not hasattr(citizen, "training_records"):
            citizen.training_records = {}
        if not hasattr(citizen, "qualifications"):
            citizen.qualifications = []
        if not hasattr(citizen, "country"):
            citizen.country = "South Africa"
        if not hasattr(citizen, "learning_goal"):
            citizen.learning_goal = "Become a master in a chosen field"

    def level(self, score: float) -> str:
        idx = min(len(self.MASTERY) - 1, max(0, int(score // 12)))
        return self.MASTERY[idx]

    def train(self, citizen, competency_id: str, hours: float = 1.0, practical: bool = True) -> TrainingRecord:
        self.ensure_citizen(citizen)
        if competency_id not in self.registry.competencies:
            raise ValueError(f"Unknown competency: {competency_id}")
        c = self.registry.competencies[competency_id]
        rec = citizen.training_records.get(competency_id)
        if rec is None:
            rec = TrainingRecord(competency_id)
            citizen.training_records[competency_id] = rec
        gain = min(10.0, max(0.5, hours * (0.75 + citizen.intelligence_capability / 4560)))
        rec.score = min(100.0, rec.score + gain)
        if practical:
            rec.practical_score = min(100.0, rec.practical_score + gain * 0.85)
        rec.attempts += 1
        rec.completed = rec.score >= 70 and rec.practical_score >= 60
        rec.verified = rec.completed and rec.attempts >= 2
        citizen.mastery_scores[competency_id] = round((rec.score * 0.6 + rec.practical_score * 0.4), 2)
        citizen.knowledge_score = min(100.0, citizen.knowledge_score + gain * 0.25)
        citizen.experience_score = min(100.0, citizen.experience_score + (gain * 0.12 if practical else gain * 0.04))
        citizen.training_level = min(100, 1 + int(citizen.knowledge_score * 0.99))
        citizen.productivity = min(3.0, citizen.productivity + gain * 0.0015)
        if competency_id not in citizen.skills:
            citizen.skills.append(competency_id)
        return rec

    def assess(self, citizen, competency_id: str, knowledge: float, practical: float) -> TrainingRecord:
        self.ensure_citizen(citizen)
        if competency_id not in self.registry.competencies:
            raise ValueError(f"Unknown competency: {competency_id}")
        rec = citizen.training_records.get(competency_id) or TrainingRecord(competency_id)
        rec.score = max(rec.score, min(100.0, knowledge))
        rec.practical_score = max(rec.practical_score, min(100.0, practical))
        rec.attempts += 1
        rec.completed = rec.score >= 70 and rec.practical_score >= 60
        rec.verified = rec.completed and rec.attempts >= 2
        citizen.training_records[competency_id] = rec
        citizen.mastery_scores[competency_id] = round(rec.score * 0.6 + rec.practical_score * 0.4, 2)
        return rec

    def award_qualifications(self, citizen) -> List[str]:
        self.ensure_citizen(citizen)
        for qid, q in self.registry.qualifications.items():
            if q.country not in (citizen.country, "International"):
                continue
            if all(citizen.training_records.get(cid, TrainingRecord(cid)).verified for cid in q.competency_ids):
                if qid not in citizen.qualifications:
                    citizen.qualifications.append(qid)
        return citizen.qualifications

    def next_recommendation(self, citizen) -> str:
        self.ensure_citizen(citizen)
        candidates = sorted(self.registry.competencies.values(), key=lambda c: citizen.mastery_scores.get(c.id, 0))
        return candidates[0].id if candidates else "CORE-DIGITAL"

    def mastery(self, citizen) -> Dict[str, str]:
        self.ensure_citizen(citizen)
        return {cid: self.level(score) for cid, score in citizen.mastery_scores.items()}
