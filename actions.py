# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, timedelta, date
import random

class ActionCheckOrderStatus(Action):
    def name(self):
        return "action_check_order_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        order_id = tracker.get_slot("order_id")

        if not order_id:
            dispatcher.utter_message(response="utter_ask_order_id")
            return []

        try:
            file_path = "./datasets/orders_updated.csv"
            df = pd.read_csv(file_path)

            order_index = df[df['O_id'] == order_id].index

            if not order_index.empty:
                idx = order_index[0]
                date_str = df.at[idx, 'Date']
                date_object = datetime.strptime(date_str, "%Y-%m-%d")
                days_to_add = int(df.at[idx, 'Deli_time'])
                expected_delivery_date = date_object + timedelta(days=days_to_add)
                today = date.today()

                if expected_delivery_date.date() == today:
                    df.at[idx, 'O_status'] = "Delivered"
                    df.to_csv(file_path, index=False)
                    status = "Delivered"
                else:
                    status = df.at[idx, 'O_status']

                dispatcher.utter_message(
                    text=f"The status for order {order_id} is: {status}."
                )

            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any order with ID {order_id}.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")

        return []
    
class ActionCheckPaymentRefundStatus(Action):
    def name(self):
        return "action_check_PR_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        order_id = tracker.get_slot("order_id")

        if not order_id:
            dispatcher.utter_message(response="utter_ask_order_id")
            return []

        try:
            df = pd.read_csv("./datasets/orders_updated.csv")

            order = df[df['O_id'] == order_id]

            if not order.empty:
                
                if(order.iloc[0]['O_type'] == 'delivery'):
                    status = order.iloc[0]['P_R_status']
                    dispatcher.utter_message(
                        text=f"The payment for order {order_id} is: {status}.")
                elif(order.iloc[0]['O_type'] == 'return'):
                    status = order.iloc[0]['P_R_status']
                    dispatcher.utter_message(
                        text=f"The refund for order {order_id} is: {status}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any order with ID {order_id}.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")

        return []

class ActionPlaceOrder(Action):
    def name(self):
        return "action_place_order"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        p_name = tracker.get_slot("product_name")
        quantity = tracker.get_slot("quantity")
        
        if not p_name and not quantity:
            dispatcher.utter_message(response="utter_ask_product_details")
            return []
        if not p_name:
            dispatcher.utter_message(response="utter_ask_product_name")
            return []
        if not quantity:
            quantity = 1  # default quantity
        else:
            quantity = int(quantity)

        try:
            df = pd.read_csv("./datasets/inventory.csv")
            order_path = "./datasets/orders_updated.csv"
            df2 = pd.read_csv(order_path)

            product = df[df['product_name'].str.lower() == p_name.lower()]

            if product.empty:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any product with name {p_name}.")
                return []

            available_quantity = int(product.iloc[0]['stock_level'])

            if available_quantity < quantity:
                dispatcher.utter_message(text=f"Sorry, we only have {available_quantity} units of {p_name} in stock.")
                return []

            order_date = date.today().strftime("%Y-%m-%d")
            O_type = "delivery"
            last_order_id = df2['O_id'].iloc[-1]
            next_id = int(last_order_id[1:]) + 1
            order_id = f"O{next_id:03d}"
            p_id = product.iloc[0]['product_id']
            product_name = p_name
            product_category = product.iloc[0]['product_category']
            price = float(product.iloc[0]['price_per_piece'])
            amount = price * quantity
            delivery_time = random.randint(5, 10)
            order_status = "Pending"
            payment_status = "Pending"

            new_order = pd.DataFrame({
                'Date': [order_date],
                'O_type': [O_type],
                'O_id': [order_id],
                'P_id': [p_id],
                'P_name': [product_name],
                'P_category': [product_category],
                'Quantity': [quantity],
                'amount': [amount],
                'Deli_time': [delivery_time],
                'O_status': [order_status],
                'P_R_status': [payment_status]
            })

            df2 = pd.concat([df2, new_order], ignore_index=True)
            df2.to_csv(order_path, index=False)

            df.loc[df['product_name'].str.lower() == p_name.lower(), 'stock_level'] -= quantity
            df.to_csv("./datasets/inventory.csv", index=False)

            dispatcher.utter_message(
                text=f"Your order for {quantity} of {p_name} has been placed successfully. "
                     f"Your order ID is {order_id}. The total amount is {amount} Rs and the expected delivery time is {delivery_time} days."
            )

            return []

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")
            return []
        

class ActionReturnOrder(Action):
    def name(self):
        return "action_return_order"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        order_id = tracker.get_slot("order_id")
        
        if not order_id:
            dispatcher.utter_message(response="utter_ask_order_id")
            return []

        try:
            df = pd.read_csv("./datasets/inventory.csv")
            order_path = "./datasets/orders_updated.csv"
            df2 = pd.read_csv(order_path)

            order = df2[df2['O_id'] == order_id]

            if  order.empty:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any product with order ID {order_id}.")
                return []

            
            else:
                order_date = date.today().strftime("%Y-%m-%d")
                O_type = "return"
                last_order_id = df2['O_id'].iloc[-1]
                next_id = int(last_order_id[1:]) + 1
                order_id = f"O{next_id:03d}"
                p_id = order.iloc[0]['P_id']
                product_name = order.iloc[0]['P_name']
                product_category = order.iloc[0]['P_category']
                quantity = order.iloc[0]['Quantity']
                amount = order.iloc[0]['amount']
                delivery_time = random.randint(5, 10)
                order_status = "Pending"
                refund_status = "Pending"

                new_order = pd.DataFrame({
                    'Date': [order_date],
                    'O_type': [O_type],
                    'O_id': [order_id],
                    'P_id': [p_id],
                    'P_name': [product_name],
                    'P_category': [product_category],
                    'Quantity': [quantity],
                    'amount': [amount],
                    'Deli_time': [delivery_time],
                    'O_status': [order_status],
                    'P_R_status': [refund_status]
                })

                df2 = pd.concat([df2, new_order], ignore_index=True)
                df2.to_csv(order_path, index=False)

                df.loc[df['product_name'].str.lower() == product_name.lower(), 'stock_level'] += quantity
                df.to_csv("./datasets/inventory.csv", index=False)

                dispatcher.utter_message(
                    text=f"Your return request for {quantity} units of {product_name} has been accepted. "
                        f"Your return ID is {order_id}. The total refund amount of {amount}rs has been initiated and an agent will collect the item from you in {delivery_time} days."
                )

            return []

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")
            return []
