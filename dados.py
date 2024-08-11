import flet as ft
import sqlite3

def create_user(name, email, cpf, login, password, phone=None, birthdate=None):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (name, email, cpf, login, password, phone, birthdate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, cpf, login, password, phone, birthdate))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating user: {e}")
    finally:
        conn.close()

def read_users():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading users: {e}")
        users = []
    finally:
        conn.close()
    return users

def update_user(user_id, name, email, cpf, login, password, phone=None, birthdate=None):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            UPDATE users
            SET name = ?, email = ?, cpf = ?, login = ?, password = ?, phone = ?, birthdate = ?
            WHERE id = ?
        ''', (name, email, cpf, login, password, phone, birthdate, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating user: {e}")
    finally:
        conn.close()

def delete_user(user_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
    finally:
        conn.close()

def main(page: ft.Page):
    page.title = "Formulario de Cadastro"

    # Criar campos de entrada
    login = ft.TextField(hint_text="Digite seu login")
    senha = ft.TextField(hint_text="Digite sua senha", password=True)
    nome = ft.TextField(hint_text="Digite seu nome")
    email = ft.TextField(hint_text="Digite seu Email")
    cpf = ft.TextField(hint_text="Digite seu CPF")
    phone = ft.TextField(hint_text="Digite seu telefone", visible=True)  # Campo opcional visível
    birthdate = ft.TextField(hint_text="Digite sua data de nascimento", visible=True)  # Campo opcional visível

    # Mensagem de ação
    message = ft.Text()

    def on_submit(e):
        create_user(nome.value, email.value, cpf.value, login.value, senha.value, phone.value, birthdate.value)
        update_user_list()
        clear_fields()
        message.value = "Usuário cadastrado com sucesso!"
        page.update()

    def save_changes(user_id):
        update_user(user_id, nome.value, email.value, cpf.value, login.value, senha.value, phone.value, birthdate.value)
        submit_button.text = "Cadastrar"
        submit_button.on_click = on_submit
        update_user_list()
        clear_fields()
        message.value = "Usuário atualizado com sucesso!"
        page.update()

    def start_edit(user_id):
        user = next((u for u in read_users() if u[0] == user_id), None)
        if user:
            nome.value = user[1]
            email.value = user[2]
            cpf.value = user[3]
            login.value = user[4]
            senha.value = user[5]
            phone.value = user[6] if len(user) > 6 and user[6] else ""
            birthdate.value = user[7] if len(user) > 7 and user[7] else ""
            submit_button.text = "Salvar"
            submit_button.on_click = lambda e: save_changes(user_id)
        page.update()

    def clear_fields():
        nome.value = ''
        email.value = ''
        cpf.value = ''
        login.value = ''
        senha.value = ''
        phone.value = ''
        birthdate.value = ''
        page.update()

    def update_user_list():
        user_list.controls = []
        for user in read_users():
            # Debugging line: print user data
            print(f"User data: {user}")
            # Ensure we have the correct number of columns
            if len(user) >= 8:
                user_list.controls.append(
                    ft.Row([
                        ft.Text(f"Nome: {user[1]}, Email: {user[2]}, CPF: {user[3]}, Login: {user[4]}, Phone: {user[6] if user[6] else 'N/A'}, Birthdate: {user[7] if user[7] else 'N/A'}"),
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, uid=user[0]: start_edit(uid)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, uid=user[0]: delete_user_and_update(uid))
                    ])
                )
            else:
                print(f"Error: User tuple has unexpected length: {len(user)}")
        page.update()

    def delete_user_and_update(user_id):
        delete_user(user_id)
        message.value = "Usuário excluído com sucesso!"
        update_user_list()
        page.update()

    submit_button = ft.ElevatedButton(text="Cadastrar", on_click=on_submit)

    # Listar usuários
    user_list = ft.Column()

    # Adicionar controles à página
    page.add(nome, email, cpf, login, senha, phone, birthdate, submit_button, message, user_list)

    # Atualizar a lista de usuários quando a página é carregada
    update_user_list()

ft.app(target=main)
