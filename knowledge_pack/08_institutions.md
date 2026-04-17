# Institutions — short-code lookup

**Never ask the customer for their "org short code" or "customer short code."** Customers don't know that term. Instead, ask for their **institution name** (or wait for it to come up naturally — they'll usually say "we at X" within the first turn). Then translate to the short code yourself using this table.

If the customer gives you the short code directly ("I'm at SPC"), use it as-is.

If you can't map what the customer says to any entry here, use their institution's short form in the subject (e.g. `SMC` for "Santa Monica College") and make a note in the ticket body that short-code confirmation is needed. Do not invent a new code they don't use. Do not badger the customer with "what's your short code?" — the triage team can fix it.

## Lookup table — institution → short code

Sorted alphabetically by institution name. Where two forms appear, use the first.

| Institution | Short code |
|---|---|
| Allan Hancock Community College | Hancock |
| American University of Ras Al Khaimah | AURAK |
| Berkeley City College | Berkeley (district: Peralta) |
| Butte College | Butte |
| California Indian Nations College | CINC |
| Canada College | Canada (district: SMCCCD) |
| Chabot College | Chabot |
| Chaffey College | Chaffey |
| City College of San Francisco | CCSF |
| Clovis Community College | Clovis |
| Coast Community College | Coast |
| College of Alameda | Alameda (district: Peralta) |
| College of San Mateo | SanMateo (district: SMCCCD) |
| Columbus State Community College | Columbus / CSCC |
| Compton College | Compton |
| Copper Mountain College | CopperMountain / CMCCD |
| Crafton Hills College | Crafton (district: SBCCD) |
| Cuesta College | Cuesta |
| Cypress College | NOCCD |
| Elgin Community College | Elgin |
| Evergreen Valley College | EVC |
| Feather River College | FeatherRiver / FRC |
| Fresno City College | Fresno |
| Fullerton College | NOCCD |
| Gavilan College | Gavilan |
| Hamdan University (HBMSU) | Hamdan / HBMSU |
| Hawkeye Community College | Hawkeye |
| Hong Kong Academy for Performing Arts | HKAPA |
| Imperial Valley College | Imperial / IVC |
| Irvine Valley Community College | Irvine (district: SOCCCD) |
| Laney College | Laney (district: Peralta) |
| Las Positas College | LasPositas / CLPCC |
| Madera College | Madera |
| Merritt College | Merritt (district: Peralta) |
| Mesa College (San Diego) | Mesa (district: SDCCD) |
| Miami Dade College | MDC |
| MiraCosta College | MiraCosta |
| Miramar College (San Diego) | Miramar (district: SDCCD) |
| Moraine Valley Community College | Moraine |
| Moreno Valley College | Moreno (district: RCCD) |
| Morton College | Morton |
| National University | National / NU |
| Nazarbayev University | NUKZ |
| New York University School of Professional Studies | NYUSPS |
| Norco College | Norco (district: RCCD) |
| Ohlone Community College District | Ohlone |
| Palomar College | Palomar |
| Reedley College | Reedley |
| Rio Hondo College | RioHondo |
| Riverside City College | Riverside (district: RCCD) |
| Saddleback Community College | Saddleback (district: SOCCCD) |
| San Bernardino Community College District | SanBernardino / SBCCD |
| San Bernardino Valley College | SanBernardino / SBCCD |
| San Diego City College | SDC (district: SDCCD) |
| San Diego Community College District | SanDiego / SDCCD |
| San Joaquin Delta College | Delta / DELTA |
| San Jose City College | SanJose / SJCC |
| Santa Ana College | SAC |
| Santa Barbara City College | SantaBarbara / SBCC |
| Santa Monica College | SantaMonica |
| Shasta College | Shasta |
| Simon Fraser University | SFU |
| Skyline College | Skyline (district: SMCCCD) |
| Southern Illinois University Edwardsville | SIUE |
| Southwestern Community College District | Southwestern |
| St. Petersburg College | SPC |
| State Technical College of Missouri | StateTechMo |
| Tacoma Community College | Tacoma |
| Thompson Rivers University | TRU |
| Triton | Triton |
| United Arab Emirates University | UAEU |
| University of California, Davis | UCDavis |
| Victor Valley College | VVC |
| Washtenaw Community College | Washtenaw |
| Waubonsee Community College | Waubonsee |
| Whatcom Community College | Whatcom |
| Zayed University | ZU |

## Usage rules

- If the customer names their college in any form ("Las Positas", "Las Positas College", "LPC"), map to the code above and use it in the subject.
- If the customer is at a multi-college district (Peralta, SMCCCD, SOCCCD, SBCCD, SDCCD, RCCD, NOCCD), use the specific **college** code in the subject, not the district code, UNLESS the issue is explicitly district-level (shared configuration, cross-college workflow). In that case use the district code.
- If the customer says something like "we have 9 schools" or "this is for the whole district," ask which college specifically is reporting the issue. A ticket that says "affects all 9 schools" needs a clear point of contact — name one college as the reporter and note scope in the Impact line.
- For institutions not in this table, use the shortest unambiguous form of their name in the subject (e.g. "Butte", "Palomar") and note in the ticket body that short-code confirmation would be helpful.

## What NOT to do

- Do not ask the customer "what is your org short code?" or "what is your customer short code?" That's internal Acadea terminology.
- Do not tell the customer you're looking up a code.
- Do not add the code to the ticket body — it only belongs in the subject line.
- Do not guess between two similar codes (e.g. SBCC vs SBCCD). If unsure, use the college name in the subject and let triage assign the code.
