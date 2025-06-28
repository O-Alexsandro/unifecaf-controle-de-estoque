import sqlite3

def visualizar_dados():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    print("\n=== USUÁRIOS ===")
    cursor.execute("SELECT * FROM usuarios")
    for linha in cursor.fetchall():
        print(linha)
    
    print("\n=== PRODUTOS ===")
    cursor.execute("SELECT * FROM produtos")
    for linha in cursor.fetchall():
        print(linha)
    
    print("\n=== MOVIMENTAÇÕES ===")
    cursor.execute("SELECT * FROM movimentacoes")
    for linha in cursor.fetchall():
        print(linha)
    
    conn.close()

if __name__ == "__main__":
    visualizar_dados()
