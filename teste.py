import flet as ft
import sqlite3
import re

def create_user(name, email, cpf, login, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (name, email, cpf, login, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, cpf, login, password))
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

def update_user(user_id, name, email, cpf, login, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            UPDATE users
            SET name = ?, email = ?, cpf = ?, login = ?, password = ?
            WHERE id = ?
        ''', (name, email, cpf, login, password, user_id))
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

def validate_fields(name, email, cpf, login, password):
    errors = []
    if not name:
        errors.append("Nome é obrigatório.")
    if not email or '@' not in email:
        errors.append("Email é obrigatório e deve conter '@'.")
    if not cpf or not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        errors.append("CPF deve estar no formato 000.000.000-00.")
    if not login:
        errors.append("Login é obrigatório.")
    if not password:
        errors.append("Senha é obrigatória.")
    return errors

def format_cpf(cpf):
    digits = re.sub(r'\D', '', cpf)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return cpf

def main(page: ft.Page):
    page.title = "Formulario de Cadastro"

    # Criar campos de entrada
    login = ft.TextField(hint_text="Digite seu login")
    senha = ft.TextField(hint_text="Digite sua senha", password=True)
    nome = ft.TextField(hint_text="Digite seu nome")
    email = ft.TextField(hint_text="Digite seu Email")
    cpf = ft.TextField(hint_text="Digite seu CPF")

    # Mensagem de ação
    message = ft.Text()

    def on_submit(e):
        formatted_cpf = format_cpf(cpf.value)
        errors = validate_fields(nome.value, email.value, formatted_cpf, login.value, senha.value)
        if errors:
            message.value = "\n".join(errors)
            page.update()
            return
        
        create_user(nome.value, email.value, formatted_cpf, login.value, senha.value)
        message.value = "Usuário cadastrado com sucesso!"
        update_user_list()
        clear_fields()

    def save_changes(user_id):
        formatted_cpf = format_cpf(cpf.value)
        errors = validate_fields(nome.value, email.value, formatted_cpf, login.value, senha.value)
        if errors:
            message.value = "\n".join(errors)
            page.update()
            return
        
        update_user(user_id, nome.value, email.value, formatted_cpf, login.value, senha.value)
        submit_button.text = "Cadastrar"
        submit_button.on_click = on_submit
        message.value = "Usuário atualizado com sucesso!"
        update_user_list()
        clear_fields()

    def start_edit(user_id):
        user = next((u for u in read_users() if u[0] == user_id), None)
        if user:
            nome.value = user[1]
            email.value = user[2]
            cpf.value = user[3]
            login.value = user[4]
            senha.value = user[5]
            submit_button.text = "Salvar"
            submit_button.on_click = lambda e: save_changes(user_id)
        page.update()

    def clear_fields():
        nome.value = ''
        email.value = ''
        cpf.value = ''
        login.value = ''
        senha.value = ''
        page.update()

    def update_user_list():
        user_list.controls = []
        for user in read_users():
            # Debugging line: print user data
            print(f"User data: {user}")
            # Ensure we have the correct number of columns
            if len(user) >= 6:
                user_list.controls.append(
                    ft.Row([
                        ft.Text(f"Nome: {user[1]}, Email: {user[2]}, CPF: {user[3]}, Login: {user[4]}"),
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
    page.add(nome, email, cpf, login, senha, submit_button, message, user_list)

    # Atualizar a lista de usuários quando a página é carregada
    update_user_list()

ft.app(target=main)