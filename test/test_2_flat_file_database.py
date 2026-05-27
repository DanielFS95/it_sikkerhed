import json
import os
import pytest
from src.flat_file.data_handler import Data_handler
from src.flat_file.user import User

pytestmark = pytest.mark.focus
test_file_name = "db_flat_file_test.json"


# helpers
def create_json_file(filename: str, content: dict):
    """Helper til at oprette test-jsonfiler."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def delete_json_files():
    filename = test_file_name
    if os.path.exists(filename):
        os.remove(filename)

# setup / cleanup step for each test
@pytest.fixture(scope="function", autouse=True)
def cleanup_files():
    # before test
    delete_json_files()
    yield
    # after test
    delete_json_files()


# ─── TESTS ───────────────────────────────────────────────────────────────────
# Teknik: Tilstandsbaseret test + ækvivalenspartitionering
# Risiko hvis testen fejler: Brugere kan ikke oprettes eller hentes → login virker ikke

def test_create_and_find_user():
    # Given – tom database
    data_handler = Data_handler(test_file_name)
    assert data_handler.get_number_of_users() == 0

    # When – opretter én bruger
    data_handler.create_user("John", "Doe", "Main Street", "10", "secret")

    # Then – brugeren kan hentes og har korrekte felter
    assert data_handler.get_number_of_users() == 1
    user: User = data_handler.get_user_by_id(0)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.address == "Main Street"
    assert user.street_number == "10"
    assert user.password == "secret"
    assert user.enabled is True


# Teknik: Tilstandsbaseret test (enable/disable tilstandsmaskine)
# Risiko hvis testen fejler: Deaktiverede brugere kan stadig logge ind

def test_disable_and_enable_user():
    # Given – to brugere, begge aktive
    data_handler = Data_handler(test_file_name)
    data_handler.create_user("John", "Doe", "Main Street", "11", "secret")
    data_handler.create_user("Jane", "Doe", "Oak Avenue", "12", "secret2")
    assert data_handler.get_number_of_users() == 2
    user0: User = data_handler.get_user_by_id(0)
    user1: User = data_handler.get_user_by_id(1)
    assert user0.enabled is True
    assert user1.enabled is True

    # When – deaktiverer bruger 0
    data_handler.disable_user(0)

    # Then – kun bruger 0 er deaktiveret
    assert user0.enabled is False
    assert user1.enabled is True

    # When – deaktiverer bruger 1 og genaktiverer bruger 0
    data_handler.disable_user(1)
    data_handler.enable_user(0)

    # Then – bruger 0 er aktiv, bruger 1 er deaktiveret
    assert user0.enabled is True
    assert user1.enabled is False


# Teknik: Ækvivalenspartitionering – ugyldig partition (id eksisterer ikke)
# Risiko hvis testen fejler: Systemet krasher ved opslag på ukendt bruger-id

def test_get_user_with_nonexistent_id_returns_none():
    # Given – tom database
    data_handler = Data_handler(test_file_name)

    # When – forsøger at hente bruger med id der ikke eksisterer
    result = data_handler.get_user_by_id(999)

    # Then – returnerer None uden at kaste exception
    assert result is None


# Teknik: Grænseværdianalyse – id=0 (mindste gyldige id)
# Risiko hvis testen fejler: Den første bruger kan ikke hentes (off-by-one fejl)

def test_get_first_user_by_boundary_id():
    # Given – én bruger oprettet med id=0
    data_handler = Data_handler(test_file_name)
    data_handler.create_user("Alice", "Smith", "Park Lane", "1", "pw123")

    # When – henter bruger med id=0 (grænseværdi)
    user: User = data_handler.get_user_by_id(0)

    # Then – brugeren findes og har korrekt id
    assert user is not None
    assert user.person_id == 0


# Teknik: Ækvivalenspartitionering – auto-increment af person_id
# Risiko hvis testen fejler: Brugere får duplikerede id'er → databasekorruption

def test_multiple_users_get_unique_sequential_ids():
    # Given – tom database
    data_handler = Data_handler(test_file_name)

    # When – opretter tre brugere
    data_handler.create_user("Alice", "A", "Street A", "1", "pw1")
    data_handler.create_user("Bob", "B", "Street B", "2", "pw2")
    data_handler.create_user("Carol", "C", "Street C", "3", "pw3")

    # Then – brugerne har unikke, sekventielle id'er
    assert data_handler.get_user_by_id(0).first_name == "Alice"
    assert data_handler.get_user_by_id(1).first_name == "Bob"
    assert data_handler.get_user_by_id(2).first_name == "Carol"
    assert data_handler.get_number_of_users() == 3


# Teknik: Persistenstest – data gemmes og indlæses korrekt fra fil
# Risiko hvis testen fejler: Data mistes ved genstart → ingen brugere kan logge ind

def test_database_persists_and_reloads_from_file():
    # Given – opret bruger og gem til fil
    data_handler = Data_handler(test_file_name)
    data_handler.create_user("Persist", "User", "Memory Lane", "42", "saved")

    # When – opretter ny instans der læser fra samme fil
    reloaded = Data_handler(test_file_name)

    # Then – den gemte bruger er tilgængelig i ny instans
    assert reloaded.get_number_of_users() == 1
    user: User = reloaded.get_user_by_id(0)
    assert user.first_name == "Persist"
    assert user.last_name == "User"
    assert user.password == "saved"
    assert user.enabled is True


# Teknik: Ækvivalenspartitionering – opdateringsoperationer
# Risiko hvis testen fejler: Brugere kan ikke opdatere deres oplysninger

def test_update_user_fields():
    # Given – en bruger er oprettet
    data_handler = Data_handler(test_file_name)
    data_handler.create_user("Old", "Name", "Old Street", "1", "oldpass")
    user: User = data_handler.get_user_by_id(0)

    # When – opdaterer alle felter
    data_handler.update_first_name(0, "New")
    data_handler.update_last_name(0, "Surname")
    data_handler.update_address(0, "New Avenue")
    data_handler.update_street_number(0, "99")
    data_handler.update_password(0, "newpass")

    # Then – alle felter er opdateret
    assert user.first_name == "New"
    assert user.last_name == "Surname"
    assert user.address == "New Avenue"
    assert user.street_number == "99"
    assert user.password == "newpass"


# Teknik: Tilstandsbaseret test – sletning af bruger
# Risiko hvis testen fejler: Slettede brugere kan stadig logge ind (sikkerhedsrisiko)

def test_delete_user_removes_from_database():
    # Given – to brugere i databasen
    data_handler = Data_handler(test_file_name)
    data_handler.create_user("Delete", "Me", "Gone Street", "0", "bye")
    data_handler.create_user("Keep", "Me", "Stay Street", "1", "hi")
    assert data_handler.get_number_of_users() == 2

    # When – sletter bruger med id=0
    data_handler.delete_user(0)

    # Then – kun én bruger tilbage, og den slettede findes ikke
    assert data_handler.get_number_of_users() == 1
    assert data_handler.get_user_by_id(0) is None


# Teknik: Robusthedstest – operationer på ikke-eksisterende bruger
# Risiko hvis testen fejler: Systemet krasher med AttributeError ved ugyldige id'er

def test_operations_on_nonexistent_user_do_not_crash():
    # Given – tom database
    data_handler = Data_handler(test_file_name)

    # When/Then – ingen af disse kald må kaste exceptions
    data_handler.disable_user(999)
    data_handler.enable_user(999)
    data_handler.delete_user(999)
    data_handler.update_first_name(999, "X")
    data_handler.update_password(999, "X")
