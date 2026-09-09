import argparse
from .seed import seed_world
from .engine import EconomyEngine

def summary(w):
    print(f"\nAI EARTH v0.4 — Day {w.day}")
    print("="*60)
    print(f"Economy value : R{w.economy_value:,.2f}\nOwner capital : R{w.owner_capital:,.2f}\nTreasury      : R{w.treasury:,.2f}")
    print(f"Citizens      : {len(w.citizens)}\nBusinesses    : {len(w.businesses)}\nFlags         : {len(w.flags)}")
    print("\nBusinesses")
    for b in w.businesses.values():
        print(f"  {b.name:22} cash R{b.cash:8,.0f} | profit R{b.profit:8,.0f} | Q {b.quality_score:5.1f} | S {b.safety_score:5.1f} | {b.status}")
    print("\nRecent AI decisions/events")
    for e in w.events[-12:]:
        amount = f" R{e.amount:,.0f}" if e.amount else ""
        print(f"  Day {e.day:03} [{e.kind:10}] {e.message}{amount}")
    if w.flags:
        print("\nOversight flags")
        for f in w.flags[-8:]: print("  !", f)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=1)
    p.add_argument("--interactive", action="store_true")
    args = p.parse_args()
    w = seed_world(); engine = EconomyEngine(w)
    if args.interactive:
        while True:
            summary(w)
            cmd = input("\nCommand [day/status/quit]: ").strip().lower()
            if cmd in {"quit", "q", "exit"}: break
            if cmd in {"day", "d", ""}: engine.advance_day()
    else:
        for _ in range(max(0, args.days)): engine.advance_day()
        summary(w)

if __name__ == "__main__": main()
