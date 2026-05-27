# What is this repository for?
This is for teaching advanced network class on Zealand Business Academy (zealand.dk)

---

## Flat File Database (JSON)

### Hvorfor er det smart at bruge en flat file database?

En flat file database gemmer data direkte i en JSON-fil på disken. Det har flere fordele i undervisnings- og prototypekontekster:

- **Ingen opsætning** – ingen databaseserver, ingen driver, ingen forbindelsesstreng. Man starter koden og alt virker.
- **Menneskelæsbart format** – JSON-filen kan åbnes i en teksteditor og man kan med det samme se, hvad der er gemt.
- **Portabilitet** – databasefilen kan kopieres, deles eller commites til Git.
- **Simpel debugging** – hvis noget går galt, åbner man bare filen og ser præcis, hvad der ligger der.
- **Godt udgangspunkt** – man forstår persistence-mekanismen fra bunden, inden man skifter til en rigtig database som SQLite eller PostgreSQL.

**Begrænsninger:** Ikke egnet til produktion – ingen transaktioner, ingen concurrent write-sikkerhed, skalerer ikke til mange brugere.

---

### Brugerdatabasens felter

```
person_id | first_name | last_name | address | street_number | password | enabled
```

---

## Installation (Before running test)

```
pip install amqtt asyncio paho-mqtt pytest-timeout fastapi uvicorn python-multipart httpx jinja2 AsyncClient pytest-asyncio Crypto python-jose python-dotenv cryptography pyjwt python-json-logger
```

---

## Run in terminal:

```
pytest -v -s
```

Kør kun flat file tests:

```
pytest test/test_2_flat_file_database.py -v -s
```

## Run in VSCodium:

- `[shift]+[ctrl]+b` og vælg `pytest run all`
- Brug `@pytest.mark.focus` og vælg `pytest focus` for kun at køre den markerede test

---

## Unit tests – flat file database

Testfilens placering: `test/test_2_flat_file_database.py`

### Anvendte testdesignteknikker

| Test | Teknik | Risiko hvis fejl |
|------|--------|-----------------|
| `test_create_and_find_user` | Tilstandsbaseret | Login virker ikke – ingen brugere kan oprettes |
| `test_disable_and_enable_user` | Tilstandsmaskine | Deaktiverede brugere kan logge ind (sikkerhedsbrist) |
| `test_get_user_with_nonexistent_id_returns_none` | Ækvivalenspartitionering (ugyldig) | Systemet krasher ved opslag på ukendt id |
| `test_get_first_user_by_boundary_id` | Grænseværdianalyse (id=0) | Off-by-one fejl – første bruger kan ikke hentes |
| `test_multiple_users_get_unique_sequential_ids` | Ækvivalenspartitionering | Duplikerede id'er → databasekorruption |
| `test_database_persists_and_reloads_from_file` | Persistenstest | Data mistes ved genstart → ingen kan logge ind |
| `test_update_user_fields` | Ækvivalenspartitionering (opdatering) | Brugere kan ikke opdatere profil |
| `test_delete_user_removes_from_database` | Tilstandsbaseret (sletning) | Slettede brugere kan stadig logge ind |
| `test_operations_on_nonexistent_user_do_not_crash` | Robusthedstest | Systemet krasher med AttributeError |

### Struktur i test cases

Alle test cases følger **Given / When / Then**-mønsteret:

```python
def test_create_and_find_user():
    # Given – tom database
    data_handler = Data_handler(test_file_name)
    assert data_handler.get_number_of_users() == 0

    # When – opretter én bruger
    data_handler.create_user("John", "Doe", "Main Street", "10", "secret")

    # Then – brugeren kan hentes og har korrekte felter
    user: User = data_handler.get_user_by_id(0)
    assert user.first_name == "John"
    assert user.enabled is True
```

---

## Kryptering og Hashing

Kode: `src/flat_file/encryption_service.py`

### Hvilke algoritmer var til rådighed?

Fra benchmark-testen (`test_1_encryption_benchmark.py`) blev følgende testet:

| Algoritme | Type | Nøglelængde |
|-----------|------|-------------|
| AES-128 (EAX) | Symmetrisk | 128 bit |
| **AES-256 (EAX)** | **Symmetrisk** | **256 bit** |
| Blowfish-128 (CBC) | Symmetrisk | 128 bit |
| Blowfish-448 (CBC) | Symmetrisk | 448 bit |
| RSA-2048 | Asymmetrisk | 2048 bit |
| SHA2-256 / SHA3-256 | Hashing | – |
| HMAC-SHA256 | Hashing m. nøgle | – |

### Valgte algoritmer og begrundelse

**Kryptering: AES-256 i EAX-tilstand**
- AES-256 er industristandarder og godkendt til klassificerede data (NSA Suite B)
- EAX-tilstand giver *authenticated encryption* – giver både fortrolighed og integritetsbeskyttelse i ét trin
- RSA valgte vi fra, da det er asymmetrisk og beregnet til nøgleudveksling, ikke bulk-kryptering af database-felter
- Blowfish er ældre og har en lille blokstørrelse (64 bit) der giver risiko for birthday-angreb

**Hashing: HMAC-SHA256 med tilfældig salt (16 bytes)**
- SHA3 er stærkest kryptografisk set, men HMAC-SHA256 med salt er standardtilgangen til password-hashing i kombination med en serverhemmelighed
- Det tilfældige salt sikrer at to ens passwords altid giver forskellige hashes → rainbow-table-angreb er umulige
- HMAC bruger en hemmelig nøgle (server-side secret), som gør offline brute-force markant sværere

---

### Hvornår krypteres data – og hvorfor?

Data krypteres **når det skrives til disk** (i `save_memory_database_to_file`).

Fielterne `first_name`, `last_name`, `address` og `street_number` er persondata efter GDPR. Hvis en angriber får adgang til JSON-filen (f.eks. via server-adgang eller backup-lækage), kan de ikke læse personoplysningerne uden krypteringsnøglen.

Passwords krypteres ikke – de hashes i stedet ved oprettelse, da de aldrig behøver at gendannes til klartekst.

---

### Hvornår dekrypteres data – og hvorfor?

Data dekrypteres **når det læses fra disk** (i `load_memory_database_from_file`).

Dekryptering sker kun ved indlæsning, ikke løbende. Det betyder at systemet har dekrypteret data i RAM mens det kører – et bevidst trade-off for ydeevne. I et mere sikkert design ville man dekryptere on-demand pr. request og straks rydde.

---

### Hvornår fjernes dekrypteret data fra hukommelsen – og hvorfor?

Dekrypteret data fjernes fra hukommelsen med `clear_sensitive_data()` **efter at en operation er afsluttet**.

Hvis data ligger i RAM for længe, er det sårbart over for:
- **Memory dump-angreb** – en angriber der kan læse proceshukommelsen
- **Swap-filer** – OS kan skrive RAM til disk i klartekst

I produktionssystemer bør plaintext-data leve kortest muligt – ideelt kun i varighed af ét request.

---

### Bør du tage hensyn til andet?

- **Nøglehåndtering:** Krypteringsnøglen er i `.env`-filen. Hvis angriberen har adgang til begge (fil + nøgle), er krypteringen meningsløs. I produktion bør nøgler ligge i en ekstern key vault (f.eks. Azure Key Vault, HashiCorp Vault).
- **`person_id` og `enabled` krypteres ikke** – de anses ikke som personhenførbare.
- **GDPR kræver ikke kryptering i sig selv**, men kryptering er stærk dokumentation for "appropriate technical measures" (Art. 32).
- **Passwords gemmes aldrig i klartekst** – heller ikke i hukommelsen efter den første `create_user`-kald.
