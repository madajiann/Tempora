package completion

import "tempora/internal/evidence"

func Build(_ any, ledger *evidence.Ledger) Report { return BuildFacts(ledger, "", nil) }
