import database
import os
import cipher
import environHandler

ENV_FILE = "environVars.csv"
SALT1 = "sd98u9b893hgb09ufb89n120u98sbu-jauisfh9usdgnsf"
SALT2 = "12b0g9bud8b98sjboi019j98h98b2ugioer8u89dbu0"
SALTED_STR = SALT1 + ENV_FILE + SALT2

ciph = cipher.Cipher(SALTED_STR)

environHandler.load_env_from_csv(ENV_FILE)

db = database.Database(
    database_name=os.getenv("DBDatabaseName"),
    root_username=ciph.decrypt(os.getenv("DBRootUsername")),
    root_password=ciph.decrypt(os.getenv("DBRootPassword")),
    host=os.getenv("DBHost")
).root_connect()

print(db.execute("DELETE FROM users WHERE user_id = 6"))
