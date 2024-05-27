import streamlit as st
import pandas as pd
import math

CANDIDATES = ["Pepperoni", "Brocolli", "Cheese"]

def _write_output(res, col_name, header):
    res_df = pd.DataFrame.from_dict(res, orient='index', columns=[col_name])
    res_df = res_df.sort_values(by = col_name,axis=0, ascending=False)
    st.subheader(header)
    st.dataframe(res_df, use_container_width=True)
    st.divider()


def create_preference_form(player_name, options, max_points):
    st.subheader(f"Preference form for {player_name}")
    
    N = len(options)
    columns = st.columns(2)  
    preferences = []
    allocated_points = []

    with columns[0]:
        st.write("Ranking")
        for i in range(N):
            preference = st.selectbox(
                label=f"Rank {i+1}",
                options=options,
                key=f"{player_name}_rank_{i}",
                index=None
            )
            preferences.append(preference)
    
    with columns[1]:
        st.write("Points")
        for i in range(N):
            points = st.number_input(
                label=f"Points for {options[i]}",
                min_value=0,
                max_value=max_points,
                key=f"{player_name}_points_{i}"
            )
            allocated_points.append((options[i], points))
    
    # Check for duplicates in ranking
    if len(set(preferences)) != len(preferences):
        st.write("You have duplicates in your ranking!")
    
    # Sum of allocated points
    total_allocated_points = sum([points for _, points in allocated_points])
    if total_allocated_points != max_points:
        st.write(f"Total points allocated: {total_allocated_points}. Please allocate exactly {max_points} points.")
    
    return preferences, allocated_points



def _compute_borda(all_preferences):
    res = {candidate:0 for candidate in CANDIDATES}
    for player in all_preferences:
        for k, v in all_preferences[player].items():
            res[k] += v
    _write_output(res, col_name="Borda Count", header= "Borda")



def _compute_quadratic(all_allocated_points):
    res = {candidate:0 for candidate in CANDIDATES}
    for player in all_allocated_points:
        for allocated_points in all_allocated_points[player]:
            quadratic_points = math.floor(math.sqrt(allocated_points[1]))
            res[allocated_points[0]] += quadratic_points
    _write_output(res, col_name="Votes", header="Quadratic Vote Results")


def _compute_plurality(all_preferences):
    plurality_res ={}
    for player in all_preferences:
        for k, v in all_preferences[player].items():
            if v == 0:
                plurality_res[player] = k
    
    # TODO: clean up this code
    df = pd.DataFrame.from_dict(plurality_res, orient='index', columns=['Choice'])
    st.subheader("Plurality Winner(s)")
    counts = df.value_counts(sort=True)
    st.dataframe(counts, use_container_width=True)
    st.divider()


def _compute_ky(all_preferences):
    pass

def _compute_condorcet(all_preferences):
    res = {}
    # check if any none values, or any duplicates
    for player in all_preferences:
        if len(set(all_preferences[player])) != len(all_preferences[player]) or None in all_preferences[player]:
            st.subheader("Waiting for Votes to be completed (& valid).")
            return
    
    # convert to rankings
    for player in all_preferences:
        all_preferences[player] = {value : index for index, value in enumerate(all_preferences[player])}

    # perform the n^2 comparison
    for focal_candidate in CANDIDATES:
        wins = 0
        for comparison_candidate in CANDIDATES:
            for player in all_preferences:
                if all_preferences[player][focal_candidate] < all_preferences[player][comparison_candidate]:
                    wins += 1

        res[focal_candidate] = wins

    _write_output(res, col_name="Wins", header="Concordet Winner(s)")


def compute_result(all_preferences, all_allocated_points, player_names, max_points):
    # check that things are okay
    if len(set(player_names)) != len(player_names):
        st.write("Make sure each player name is unique.")
        return
    for player in all_preferences:
        if len(set(all_preferences[player])) != len(all_preferences[player]) or None in all_preferences[player]:
            st.subheader("Waiting for Votes to be completed (& valid).")
            return
    
    for player in all_allocated_points:
        allocated_points = all_allocated_points[player]
        if sum([points for _, points in allocated_points]) != max_points:
            st.subheader("Waiting for Votes to be completed (& valid).")
            return

    
    # calulcate condorcet result
    _compute_condorcet(all_preferences)
    _compute_plurality(all_preferences)
    _compute_borda(all_preferences)
    _compute_quadratic(all_allocated_points)
    _compute_ky(all_preferences)
    


def main():
    st.title("Mathematics of Social Choice")
    st.caption("Pizza Topping Showdown: Discover How Voting Algorithms Spice Up Your Choices!")
    st.caption("Ever wondered how different social choice algorithms can change the outcome of a group decision? Our app lets you simulate votes with friends, rank your top pizza toppings, and see the effects of popular algorithms. Dive into the world of voting systems with a fun and delicious twist.")
    columns = st.columns(2)
    # Input: Number of people playing
    with columns[0]:
        num_people = st.number_input("Enter the number of people playing:", min_value=1, step=1)
    with columns[1]:
        max_points = st.number_input("Enter the points allocated to each player", min_value=10)

    # Dynamic input fields for player names
    player_names = []
    for i in range(num_people):
        player_name = st.text_input(f"Enter name for player {i + 1}:", value=f"Player {i+1}")
        player_names.append(player_name)
    
    all_preferences = {}
    all_allocted_points = {}
    for player in player_names:
        preferences, allocated_points = create_preference_form(player, CANDIDATES, max_points=max_points)
        all_allocted_points[player] = allocated_points
        all_preferences[player] = preferences
        preferences = [f'{e}' for e in preferences]
        order_str = " > ".join(preferences)
        st.write(f"{player}'s current preferences: {order_str}")
        st.divider()

    compute_result(all_preferences, all_allocted_points, player_names, max_points)

if __name__ == "__main__":
    main()
