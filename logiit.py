import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QSpinBox, QRadioButton, QButtonGroup, QHeaderView
from PyQt5.QtGui import QPalette, QColor, QBrush, QImage
from PyQt5.QtCore import Qt
import pandas as pd
from PyQt5.QtWebEngineWidgets import QWebEngineView
from threading import Thread
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import sqlite3
import pandas as pd
import sys
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import os 
from datetime import datetime, timedelta
from PyQt5.QtGui import QColor, QCursor 
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect


CONFIG_FILE = 'config.txt' 

def save_first_use_date(): 
    if not os.path.exists(CONFIG_FILE): 
        with open(CONFIG_FILE, 'w') as f: 
            f.write(datetime.now().isoformat())
        
def get_first_use_date(): 
    if os.path.exists(CONFIG_FILE): 
        with open(CONFIG_FILE, 'r') as f: 
            date_str = f.read().strip() 
            return datetime.fromisoformat(date_str) 
    return None

def check_subscription_needed(): 
    first_use_date = get_first_use_date() 
    if first_use_date: 
        if datetime.now() >= first_use_date + timedelta(weeks=2): 
            return True 
    return False


# Créer la base de données SQLite
def create_db():
    conn = sqlite3.connect('gestion_donnees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS produits (nom TEXT, quantite INTEGER, prix REAL, categorie TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vente (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT, sell_quantite INTEGER, new_quantite INTEGER, compte REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chiffre_d_affaire (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT, quantite INTEGER, total_prix REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS commande (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT, quantite INTEGER, total_prix REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS achat (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT, quantite INTEGER, total_prix REAL, categorie, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()


class DataLoadThread(QThread):
    data_loaded = pyqtSignal(pd.DataFrame)

    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        conn = sqlite3.connect('gestion_donnees.db')
        df = pd.read_sql_query(self.query, conn)
        conn.close()
        self.data_loaded.emit(df)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle('Connexion')
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        
        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Nom d\'utilisateur')
        layout.addWidget(self.username)
        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Mot de passe')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        
        login_btn = QPushButton('Connexion', self)
        login_btn.clicked.connect(self.check_login)
        layout.addWidget(login_btn)  
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 224))
        image = QImage(r'concept.jpg')
        scaled_image = image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_image))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
# Appliquer les styles
        login_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 16px;
                color: white;
                background-color: green;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                cursor: pointer;
                transition: box-shadow 0.3s ease;
            }
            QPushButton:hover {
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            }
        """)
        
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect 
        shadow = QGraphicsDropShadowEffect() 
        shadow.setBlurRadius(10) 
        shadow.setColor(QColor(0, 0, 0, 150)) 
        shadow.setOffset(0, 4)
        login_btn.setGraphicsEffect(shadow)
        
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        animation = QPropertyAnimation(login_btn, b"geometry") 
        animation.setDuration(300) 
        animation.setStartValue(QRect(50, 50, 200, 50)) 
        animation.setEndValue(QRect(50, 50, 200, 60)) 
        login_btn.clicked.connect(lambda: animation.start()) 
        
        layout.addWidget(login_btn)
        self.setLayout(layout)
        
    def check_login(self):
        if self.username.text() == 'admin' and self.password.text() == '1234':
            self.open_main_window()
        
    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        
from PyQt5.QtWidgets import QStackedWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gestion de Caisse')
        self.setGeometry(100, 100, 1400, 1200)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.vente_window = VenteWindow()
        self.stacked_widget.addWidget(self.vente_window)
        
        self.command_window = CommandWindow()
        self.stacked_widget.addWidget(self.command_window)
        
        self.stock_window = StockWindow()
        self.stacked_widget.addWidget(self.stock_window)
        
        self.rapport_window = RapportWindow()
        self.stacked_widget.addWidget(self.rapport_window)
        
        self.predict_window = PredictWindow()
        self.stacked_widget.addWidget(self.predict_window)
        
        menu_layout = QVBoxLayout()
        
        button1 = QPushButton('Gérer les Ventes', self)
        button1.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.vente_window))
        menu_layout.addWidget(button1)
        
        button1 = QPushButton('Ajouter une Commande', self)
        button1.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.command_window))
        menu_layout.addWidget(button1)
        
        button2 = QPushButton('Gérer le Stock', self)
        button2.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.stock_window))
        menu_layout.addWidget(button2)
        
        button3 = QPushButton('Ouvrir Rapports', self)
        button3.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.rapport_window))
        menu_layout.addWidget(button3)
        
        button4 = QPushButton('Rapports sur nos prévisions', self)
        button4.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.predict_window))
        menu_layout.addWidget(button4)
        
        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(menu_widget)
        splitter.addWidget(self.stacked_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
        
        close_btn = QPushButton('Fermer l\'application', self)
        close_btn.clicked.connect(self.close_application)
        menu_layout.addWidget(close_btn)

    # ... [les autres méthodes]
        
        # Appliquer les styles
        self.setStyleSheet("""
        QLabel {
            font-size: 18px;
            padding: 10px;
        }
        QPushButton {
                padding: 10px 20px;
                font-size: 16px;
                color: white;
                background-color: green;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                cursor: pointer;
                transition: box-shadow 0.3s ease;
            }
            QPushButton:hover {
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            }
        QHBoxLayout, QVBoxLayout {
            margin: 10px;
            background-color: orange;
        }
        QWidget {
            background-repeat: no-repeat;
            background-position: center;
        }
        """)
        
    def show_subscription_prompt(self): 
        msg_box = QMessageBox(self) 
        msg_box.setWindowTitle("Abonnement Requis") 
        msg_box.setText("Votre période d'essai de 2 semaines est terminée. Veuillez vous abonner pour continuer à utiliser l'application.") 
        msg_box.setIcon(QMessageBox.Information) 
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def vente_window(self): 
        self.clear_content() 
        vente_window = VenteWindow() 
        self.content_layout.addWidget(vente_window)
        
    def command_window(self): 
        self.clear_content() 
        command_window = CommandWindow() 
        self.content_layout.addWidget(command_window)
        
    def stock_window(self): 
        self.clear_content() 
        stock_window = StockWindow() 
        self.content_layout.addWidget(stock_window) 
    def rapport_window(self): 
        self.clear_content() 
        rapport_window = RapportWindow() 
        self.content_layout.addWidget(rapport_window) 
    
    def predict_window(self): 
        self.clear_content() 
        predict_window = PredictWindow() 
        self.content_layout.addWidget(predict_window)
    
    def clear_content(self): 
        # Effacer les widgets existants dans content_widget 
        for i in reversed(range(self.content_layout.count())): 
            widget = self.content_layout.itemAt(i).widget() 
            if widget is not None: 
                widget.setParent(None)
            
    def close_application(self):
        QApplication.instance().quit()
        
class VenteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Vente')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Nom', 'Quantité', 'Prix', 'categorie'])
        layout.addWidget(self.table)

        self.quantity_input = QSpinBox(self)
        self.quantity_input.setRange(1, 100)
        layout.addWidget(self.quantity_input)

        self.sell_button = QPushButton('Valider la vente', self)
        self.sell_button.clicked.connect(self.sell_product)
        layout.addWidget(self.sell_button)
        
        self.total_label = QLabel(self) 
        layout.addWidget(self.total_label)

        self.setLayout(layout)

        self.load_data()
        
        # Ajuster la largeur des colonnes pour remplir l'espace disponible 
        header = self.table.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.Stretch) 
        # Ajuster la hauteur des lignes pour leur contenu self
        self.table.resizeRowsToContents()
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)
        
    def load_data(self):
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom, quantite, prix, categorie FROM produits")
        products = cursor.fetchall()

        self.table.setRowCount(len(products))
        for i, (nom, quantite, prix, categorie) in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(nom))
            self.table.setItem(i, 1, QTableWidgetItem(str(quantite)))
            self.table.setItem(i, 2, QTableWidgetItem(str(prix)))
            self.table.setItem(i, 3, QTableWidgetItem(str(categorie)))
        conn.close()

    def sell_product(self):
        selected_row = self.table.currentRow()
    
        if selected_row < 0:
            print("Aucun produit sélectionné")
            return
    
        nom = self.table.item(selected_row, 0).text()
        sell_quantite = self.quantity_input.value()
        prix_unitaire = float(self.table.item(selected_row, 2).text())

        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("SELECT quantite FROM produits WHERE nom=?", (nom,))
            result = cursor.fetchone()
        
            if result is None:
                print(f"Produit '{nom}' non trouvé dans la base de données")
                return
        
            current_quantite = result[0]
        
            if current_quantite >= sell_quantite:
                new_quantite = current_quantite - sell_quantite
                cursor.execute("UPDATE produits SET quantite = ? WHERE nom = ?", (new_quantite, nom))
            
                cursor.execute("INSERT INTO vente (nom, sell_quantite, new_quantite) VALUES (?, ?, ?)", (nom, sell_quantite, new_quantite))
            
                total_prix = sell_quantite * prix_unitaire
                cursor.execute("INSERT INTO chiffre_d_affaire (nom, quantite, total_prix) VALUES (?, ?, ?)", (nom, sell_quantite, total_prix))
            
                conn.commit()
                self.total_label.setText(f"Prix total de vente: {total_prix:.2f} FCFA")
            else:
                print(f"Quantité insuffisante pour le produit '{nom}'")
    
        except sqlite3.Error as e:
            print(f"Erreur de la base de données : {e}")
    
        finally:
            conn.close()
            self.load_data()

class CommandWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Ajouter Une commande')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Nom', 'Quantité', 'Prix', 'categorie'])
        layout.addWidget(self.table)

        self.quantity_input = QSpinBox(self)
        self.quantity_input.setRange(1, 100)
        layout.addWidget(self.quantity_input)

        self.command_button = QPushButton('Valider la commande', self)
        self.command_button.clicked.connect(self.command_product)
        layout.addWidget(self.command_button)

        self.setLayout(layout)

        self.load_data()
        
        # Ajuster la largeur des colonnes pour remplir l'espace disponible 
        header = self.table.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.Stretch) 
        # Ajuster la hauteur des lignes pour leur contenu self
        self.table.resizeRowsToContents()
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)
        
    def load_data(self):
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom, quantite, prix, categorie FROM produits")
        products = cursor.fetchall()

        self.table.setRowCount(len(products))
        for i, (nom, quantite, prix, categorie) in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(nom))
            self.table.setItem(i, 1, QTableWidgetItem(str(quantite)))
            self.table.setItem(i, 2, QTableWidgetItem(str(prix)))
            self.table.setItem(i, 3, QTableWidgetItem(str(categorie)))
        conn.close()

    def command_product(self):
        selected_row = self.table.currentRow()
    
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Aucun produit sélectionné")
            return
    
        nom = self.table.item(selected_row, 0).text()
        sell_quantite = self.quantity_input.value()
        prix_unitaire = float(self.table.item(selected_row, 2).text())

        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("SELECT quantite FROM produits WHERE nom=?", (nom,))
            result = cursor.fetchone()
        
            if result is None:
                QMessageBox.warning(self, "Erreur", f"Produit '{nom}' non trouvé dans la base de données")
                return
        
            current_quantite = result[0]
        
            if current_quantite >= sell_quantite:
                new_quantite = current_quantite - sell_quantite
                cursor.execute("UPDATE produits SET quantite = ? WHERE nom = ?", (new_quantite, nom))
            
                cursor.execute("INSERT INTO vente (nom, sell_quantite, new_quantite) VALUES (?, ?, ?)", (nom, sell_quantite, new_quantite))
            
                total_prix = sell_quantite * prix_unitaire
            
                cursor.execute("INSERT INTO commande (nom, quantite, total_prix) VALUES (?, ?, ?)", (nom, sell_quantite, total_prix))
                cursor.execute("INSERT INTO chiffre_d_affaire (nom, quantite, total_prix) VALUES (?, ?, ?)", (nom, sell_quantite, total_prix))
            
                conn.commit()
            
                # Afficher le prix total avec QMessageBox
                QMessageBox.information(self, "Confirmation", f"Ajouté avec succès! Prix total de commande: {total_prix:.2f} FCFA")
            else:
                QMessageBox.warning(self, "Erreur", f"Quantité insuffisante pour le produit '{nom}'")
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur de la base de données", f"Erreur : {e}")
    
        finally:
            conn.close()
            self.load_data()
            
class StockWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Stock')
        self.setGeometry(100, 100, 800, 600)
        
        # Utiliser un QSplitter pour diviser la fenêtre
        splitter = QSplitter(Qt.Horizontal)
        
        # Créer le layout pour les menus
        menu_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout() 
        self.search_input = QLineEdit(self) 
        self.search_input.setPlaceholderText('Rechercher un produit') 
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('Rechercher', self) 
        search_btn.clicked.connect(self.search_product) 
        search_layout.addWidget(search_btn)
        
        menu_layout.addLayout(search_layout)
        
        add_btn = QPushButton('Ajouter Produit', self)
        add_btn.clicked.connect(self.show_add_window)
        menu_layout.addWidget(add_btn)

        delete_btn = QPushButton('Supprimer Produit', self)
        delete_btn.clicked.connect(self.show_delete_window)
        menu_layout.addWidget(delete_btn)
        
        view_btn = QPushButton('Voir Produits', self)
        view_btn.clicked.connect(self.show_view_window)
        menu_layout.addWidget(view_btn)
        
        achat_btn = QPushButton('Voir nos approvisions', self)
        achat_btn.clicked.connect(self.show_achat_window)
        menu_layout.addWidget(achat_btn)
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        menu_layout.addWidget(close_btn)
        
        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        
        # Créer le widget pour le contenu actif
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Ajouter les widgets au splitter
        splitter.addWidget(menu_widget)
        splitter.addWidget(self.content_widget)
        
        splitter.setStretchFactor(0, 1) # menu_widget prend 1 part 
        splitter.setStretchFactor(1, 20)
        
        # Ajouter le splitter au layout principal
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
        
    def search_product(self): 
        search_term = self.search_input.text() 
        conn = sqlite3.connect('gestion_donnees.db') 
        cursor = conn.cursor() 
        cursor.execute("SELECT nom, quantite, prix, categorie FROM produits WHERE nom LIKE ?", ('%' + search_term + '%',)) 
        products = cursor.fetchall() 
        conn.close()
        if products: 
            self.clear_content() 
            self.show_search_results(products)
        else: 
            QMessageBox.information(self, 'Résultats de la recherche', 'Aucun produit trouvé') 
            
    def show_search_results(self, products):
        search_results_widget = QTableWidget(self) 
        search_results_widget.setColumnCount(4) 
        search_results_widget.setHorizontalHeaderLabels(['Nom', 'Quantité', 'Prix', 'Catégorie']) 
        search_results_widget.setRowCount(len(products))
        
        for i, (nom, quantite, prix, categorie) in enumerate(products): 
            search_results_widget.setItem(i, 0, QTableWidgetItem(nom)) 
            search_results_widget.setItem(i, 1, QTableWidgetItem(str(quantite))) 
            search_results_widget.setItem(i, 2, QTableWidgetItem(str(prix))) 
            search_results_widget.setItem(i, 3, QTableWidgetItem(str(categorie))) 
            
        header = search_results_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        search_results_widget.resizeRowsToContents()
        
        self.content_layout.addWidget(search_results_widget)
    
    def show_add_window(self):
        self.clear_content()
        add_window = AddWindow()
        self.content_layout.addWidget(add_window)

    def show_delete_window(self):
        self.clear_content()
        delete_window = DeleteWindow()
        self.content_layout.addWidget(delete_window)
        
    def show_view_window(self):
        self.clear_content()
        view_window = ViewWindow()
        self.content_layout.addWidget(view_window)
        
    def show_achat_window(self):
        self.clear_content()
        achat_window = AchatWindow()
        self.content_layout.addWidget(achat_window)

    def clear_content(self):
        # Effacer les widgets existants dans content_widget
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Ajouter')
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Nom du produit')
        layout.addWidget(self.name_input)
        
        self.quantity_input = QLineEdit(self)
        self.quantity_input.setPlaceholderText('Quantité')
        layout.addWidget(self.quantity_input)
        
        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText('Prix')
        layout.addWidget(self.price_input)

        self.categorie_input = QLineEdit(self)
        self.categorie_input.setPlaceholderText('Catégorie')
        layout.addWidget(self.categorie_input)
        
        add_btn = QPushButton('Ajouter', self)
        add_btn.clicked.connect(self.add_product)
        layout.addWidget(add_btn)
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)
        
    def add_product(self):
        nom = self.name_input.text()
        quantite = self.quantity_input.text()
        prix = self.price_input.text()
        categorie = self.categorie_input.text()
        
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO produits (nom, quantite, prix, categorie) VALUES (?, ?, ?, ?)", (nom, quantite, prix, categorie))
        cursor.execute("INSERT INTO achat (nom, quantite, total_prix, categorie) VALUES (?, ?, ?, ?)", (nom, quantite, prix, categorie))
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Confirmation", "Ajouté avec succès!")
        
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.categorie_input.clear()

class DeleteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Supprimer Produits')
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Nom du produit à supprimer')
        layout.addWidget(self.name_input)

        delete_btn = QPushButton('Supprimer', self)
        delete_btn.clicked.connect(self.delete_product)
        layout.addWidget(delete_btn)

        delete_all_btn = QPushButton('Supprimer tous les produits', self)
        delete_all_btn.clicked.connect(self.delete_all_products)
        layout.addWidget(delete_all_btn)
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)

    def delete_product(self):
        nom = self.name_input.text()

        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produits WHERE nom = ?", (nom,))
        conn.commit()
        conn.close()

    def delete_all_products(self):
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produits")
        conn.commit()
        conn.close()

class ViewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Voir Produits')
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Nom', 'Quantité', 'Prix', 'Catégorie'])
        layout.addWidget(self.table)
        
        self.load_data()
        
        # Ajuster la largeur des colonnes pour remplir l'espace disponible 
        header = self.table.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.Stretch) 
        # Ajuster la hauteur des lignes pour leur contenu self
        self.table.resizeRowsToContents()
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)
        
    def load_data(self):
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom, quantite, prix, categorie FROM produits")
        products = cursor.fetchall()
        
        self.table.setRowCount(len(products))
        for i, (nom, quantite, prix, categorie) in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(nom))
            self.table.setItem(i, 1, QTableWidgetItem(str(quantite)))
            self.table.setItem(i, 2, QTableWidgetItem(str(prix)))
            self.table.setItem(i, 3, QTableWidgetItem(str(categorie)))
            
        conn.close()
        
class AchatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Voir nos provisions')
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Nom', 'Quantité', 'Prix', 'Catégorie'])
        layout.addWidget(self.table)
        
        self.load_data()
        
        # Ajuster la largeur des colonnes pour remplir l'espace disponible 
        header = self.table.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.Stretch) 
        # Ajuster la hauteur des lignes pour leur contenu self
        self.table.resizeRowsToContents()
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        layout.addWidget(close_btn)
        
    def load_data(self):
        conn = sqlite3.connect('gestion_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom, quantite, prix, categorie FROM achat")
        products = cursor.fetchall()
        
        self.table.setRowCount(len(products))
        for i, (nom, quantite, prix, categorie) in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(nom))
            self.table.setItem(i, 1, QTableWidgetItem(str(quantite)))
            self.table.setItem(i, 2, QTableWidgetItem(str(prix)))
            self.table.setItem(i, 3, QTableWidgetItem(str(categorie)))
            
        conn.close()

class RapportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Rapports')
        
        layout = QVBoxLayout()
        
        self.stacked_widget = QStackedWidget()
        
        self.table_window = TableWindow()  # Assurez-vous d'instancier la classe correctement
        self.graph_window = GraphWindow()
        self.commande_window = CommandeWindow()
        self.achat_window = AchatWindow()
        self.chiffredaffaire_window = ChiffreDAffaireWindow()
        
        self.stacked_widget.addWidget(self.table_window)
        self.stacked_widget.addWidget(self.graph_window)
        self.stacked_widget.addWidget(self.commande_window)
        self.stacked_widget.addWidget(self.achat_window)
        self.stacked_widget.addWidget(self.chiffredaffaire_window)
        
        layout.addWidget(self.stacked_widget)
        
        menu_layout = QVBoxLayout()
        
        
        self.button_table = QPushButton('Afficher Tableau', self)
        self.button_table.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.table_window))
        menu_layout.addWidget(self.button_table)
        
        self.button_graph = QPushButton('Afficher Graphique', self)
        self.button_graph.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.graph_window))
        menu_layout.addWidget(self.button_graph)
        
        self.button_commande = QPushButton('Afficher Commandes', self)
        self.button_commande.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.commande_window))
        menu_layout.addWidget(self.button_commande)
        
        self.button_achat = QPushButton('Afficher Achats', self)
        self.button_achat.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.achat_window))
        menu_layout.addWidget(self.button_achat)
        
        self.button_chiffre = QPushButton('Afficher Chiffre d\'Affaires', self)
        self.button_chiffre.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.chiffredaffaire_window))
        menu_layout.addWidget(self.button_chiffre)
        
        close_btn = QPushButton('Fermer', self) 
        close_btn.clicked.connect(self.close) 
        menu_layout.addWidget(close_btn)
        
        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        
        # Créer le widget pour le contenu actif
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Ajouter les widgets au splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(menu_widget)
        splitter.addWidget(self.stacked_widget)
        splitter.addWidget(self.content_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        # Ajouter le splitter au layout principal
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
        
    def table_window(self):
        self.clear_content()
        table_window = TableWindow()
        self.content_layout.addWidget(table_window)

    def graph_window(self):
        self.clear_content()
        graph_window = GraphWindow()
        self.content_layout.addWidget(graph_window)
        
    def commande_window(self):
        self.clear_content()
        commande_window = CommandeWindow()
        self.content_layout.addWidget(commande_window)
        
    def achat_window(self):
        self.clear_content()
        achat_window = AchatWindow()
        self.content_layout.addWidget(achat_window)
        
    def chiffredaffaire_window(self):
        self.clear_content()
        chiffredaffaire_window = ChiffreDAffaireWindow()
        self.content_layout.addWidget(chiffredaffaire_window)

    def clear_content(self):
        # Effacer les widgets existants dans content_widget
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                
class TableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Tableau de ventes')
        
        layout = QVBoxLayout()
        
        table_btn = QPushButton('Afficher le tableau', self)
        table_btn.clicked.connect(self.load_data)
        layout.addWidget(table_btn)
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        
        self.radio_group = QButtonGroup()
        
        self.radio_day = QRadioButton("Jour")
        self.radio_week = QRadioButton("Semaine")
        self.radio_month = QRadioButton("Mois")
        self.radio_year = QRadioButton("An")
        
        self.radio_group.addButton(self.radio_day)
        self.radio_group.addButton(self.radio_week)
        self.radio_group.addButton(self.radio_month)
        self.radio_group.addButton(self.radio_year)
        
        layout.addWidget(self.radio_day)
        layout.addWidget(self.radio_week)
        layout.addWidget(self.radio_month)
        layout.addWidget(self.radio_year)
        
        self.load_data()
        
        close_btn = QPushButton('Fermer', self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        query = "SELECT nom, SUM(sell_quantite) as total_ventes, date FROM vente GROUP BY nom, date"
        self.thread = DataLoadThread(query) 
        self.thread.data_loaded.connect(self.on_data_loaded) 
        self.thread.start()
    
    def on_data_loaded(self, df):
        self.df = df 
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.show_table()
        
    def show_table(self):
        if self.df is None: 
            print("Les données ne sont pas encore chargées.") 
            return
    
        if self.radio_day.isChecked():
            date_range = 'jour'
        elif self.radio_week.isChecked():
            date_range = 'semaine'
        elif self.radio_month.isChecked():
            date_range = 'mois'
        else:
            date_range = 'an'

        if date_range == 'jour':
            start_date = self.df['date'].max() - pd.DateOffset(days=1)
        elif date_range == 'semaine':
            start_date = self.df['date'].max() - pd.DateOffset(weeks=1)
        elif date_range == 'mois':
            start_date = self.df['date'].max() - pd.DateOffset(months=1)
        else:
            start_date = self.df['date'].max() - pd.DateOffset(years=1)
        
        filtered_df = self.df[self.df['date'] >= start_date]
    
        self.tableWidget.setRowCount(filtered_df.shape[0])
        self.tableWidget.setColumnCount(filtered_df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(filtered_df.columns)
    
        for i in range(filtered_df.shape[0]):
            for j in range(filtered_df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(filtered_df.iat[i, j])))
            
        header = self.tableWidget.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.Stretch)

    
class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Graphiques des ventes")
        
        layout = QVBoxLayout()
        
        
        graph_btn = QPushButton('Afficher Graphique', self)
        graph_btn.clicked.connect(self.load_data)
        layout.addWidget(graph_btn)

        
        self.radio_group = QButtonGroup()
        
        self.radio_week = QRadioButton("Semaine")
        self.radio_month = QRadioButton("Mois")
        self.radio_year = QRadioButton("An")
        
        self.radio_group.addButton(self.radio_week)
        self.radio_group.addButton(self.radio_month)
        self.radio_group.addButton(self.radio_year)
        
        layout.addWidget(self.radio_week)
        layout.addWidget(self.radio_month)
        layout.addWidget(self.radio_year)
        
        close_btn = QPushButton('Fermer', self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        
    def load_data(self):
        query = "SELECT nom, SUM(sell_quantite) as total_ventes, date FROM vente GROUP BY nom, date"
        self.thread = DataLoadThread(query) 
        self.thread.data_loaded.connect(self.on_data_loaded) 
        self.thread.start()
    
    def on_data_loaded(self, df):
        self.df = df 
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.show_graph()
        
    def show_graph(self):
        if self.df is None: 
            print("Les données ne sont pas encore chargées.") 
            return
        # Déterminer l'intervalle de temps sélectionné
        if self.radio_week.isChecked():
            date_range = 'semaine'
        elif self.radio_month.isChecked():
            date_range = 'mois'
        else:
            date_range = 'an'

        if date_range == 'semaine':
            start_date = self.df['date'].max() - pd.DateOffset(weeks=1)
        elif date_range == 'mois':
            start_date = self.df['date'].max() - pd.DateOffset(months=1)
        else:
            start_date = self.df['date'].max() - pd.DateOffset(years=1)
            
        filtered_df = self.df[self.df['date'] >= start_date]
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=filtered_df, x='nom', y='total_ventes', hue='nom')
        plt.title(f'Ventes par {date_range}')
        plt.xlabel('Nom')
        plt.ylabel('Total Ventes')
        plt.show()
        
class CommandeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Commandes')
        
        layout = QVBoxLayout()
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        
        self.load_data()
        
        close_btn = QPushButton('Fermer', self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def load_data(self):
        query = "SELECT nom, SUM(total_prix) as total_commande, date FROM commande GROUP BY nom, date"
        self.thread = DataLoadThread(query) 
        self.thread.data_loaded.connect(self.on_data_loaded) 
        self.thread.start()
    
    def on_data_loaded(self, df):
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

class AchatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Achats')
        
        layout = QVBoxLayout()
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        
        self.load_data()
        
        close_btn = QPushButton('Fermer', self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def load_data(self):
        query = "SELECT nom, SUM(total_prix) as total_achat, date FROM achat GROUP BY nom, date"
        self.thread = DataLoadThread(query) 
        self.thread.data_loaded.connect(self.on_data_loaded) 
        self.thread.start()
    
    def on_data_loaded(self, df):
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

class ChiffreDAffaireWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Chiffre d\'affaires')
        
        layout = QVBoxLayout()
        
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        
        self.total_label = QLabel(self) 
        layout.addWidget(self.total_label)
        
        self.load_data()
        
        close_btn = QPushButton('Fermer', self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def load_data(self):
        query = "SELECT nom, SUM(total_prix) as total_chiffre, date FROM chiffre_d_affaire GROUP BY nom, date"
        self.thread = DataLoadThread(query) 
        self.thread.data_loaded.connect(self.on_data_loaded) 
        self.thread.start()
    
    def on_data_loaded(self, df):
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        total_sum = df['total_chiffre'].sum()
        
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.total_label.setText(f"Total des chiffres d'affaires : {total_sum:.2f} FCFA")

class PredictionThread(QThread):
    predictions_ready = pyqtSignal(dict)

    def __init__(self, model, df, parent=None):
        super().__init__(parent)
        self.model = model
        self.df = df

    def run(self):
        # Préparation des données futures
        future_days = pd.DataFrame({'day_of_year': range(1, 366)})
        future_predictions = self.model.predict(future_days)
        
        # Créer un DataFrame pour les prévisions futures
        prediction_df = pd.DataFrame({
            'day_of_week': range(1, 366),
            'prediction': future_predictions
        })
        
        # Grouper par 'nom' et obtenir les top_sellers et low_sellers
        top_sellers = self.df.groupby('nom')['sell_quantite'].sum().sort_values(ascending=False).head(10)
        low_sellers = self.df.groupby('nom')['sell_quantite'].sum().sort_values().head(10)
        
        recommendations = {
            'top_sellers': top_sellers.to_dict(),
            'low_sellers': low_sellers.to_dict()
        }
        
        self.predictions_ready.emit(recommendations)

# Exemple d'utilisation dans une fenêtre PyQt5
class PredictWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Rapports')
        
        layout = QVBoxLayout()
        
        self.button_predict = QPushButton('Prévoir les ventes', self)
        self.button_predict.clicked.connect(self.predict_sales)
        layout.addWidget(self.button_predict)
        
        self.top_sellers_label = QLabel(self)
        layout.addWidget(self.top_sellers_label)
        
        self.low_sellers_label = QLabel(self)
        layout.addWidget(self.low_sellers_label)
        
        self.setLayout(layout)
        
    def load_sales_data(self):
        conn = sqlite3.connect('gestion_donnees.db')
        query = "SELECT nom, sell_quantite, date FROM vente"
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['date'] = pd.to_datetime(df['date'])
        return df

    def train_model(self, df):
        df['day_of_year'] = df['date'].dt.dayofyear
        X = df[['day_of_year']]
        y = df['sell_quantite']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X, y)
        return model

    def predict_sales(self):
        sales_data = self.load_sales_data()
        model = self.train_model(sales_data)
        
        self.thread = PredictionThread(model, sales_data)
        self.thread.predictions_ready.connect(self.show_predictions)
        self.thread.start()
        
    def show_predictions(self, recommendations):
        top_sellers = recommendations['top_sellers']
        low_sellers = recommendations['low_sellers']
        
        top_sellers_text = "Produits les plus vendus :\n" + "\n".join([f"{k}: {v:.2f}" for k, v in top_sellers.items()])
        low_sellers_text = "Produits les moins vendus :\n" + "\n".join([f"{k}: {v:.2f}" for k, v in low_sellers.items()])
        
        self.top_sellers_label.setText(top_sellers_text)
        self.low_sellers_label.setText(low_sellers_text)


if __name__ == '__main__':
    save_first_use_date()
    create_db()
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

