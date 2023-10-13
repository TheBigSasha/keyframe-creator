import pandas as pd

def main():
    running = True
    df = pd.DataFrame(columns=["x", "y", "z", "alpha", "beta", "gamma", "duration"])
    while running:
            print("Enter the follwing comma separated values: ")
            print("x, y, z, alpha, beta, gamma, duration")
            print("Enter 'q' to quit and save")
            user_input = input()
            if user_input == "q":
                running = False
                print("Enter filename to save to: ")
                filename = input()
                df.to_csv(filename + ".csv")
                break
            else:
                try:
                    user_input = user_input.split(",")
                    user_input = [float(i) for i in user_input]
                    df.loc[-1] = user_input
                    print(df)
                except ValueError:
                    print("Invalid input")
                    continue
                except Exception as e:
                    print(e)
                    continue
                else:
                    print("Valid input")
                    continue
    print("Exiting")

if __name__ == "__main__":
    main()
