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





<img width="984" height="488" alt="image" src="https://github.com/user-attachments/assets/f33d12e0-7775-4b25-9e0a-409577c4a50c" />
