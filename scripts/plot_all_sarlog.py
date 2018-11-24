import sys,os
import sar
from sar import parser
from sarviz import viz


def main():
	directory = os.path.dirname(os.path.realpath(__file__))
	for item in os.listdir(directory):
		full_path = os.path.join(directory, item)
		if os.path.isfile(full_path) and item != __file__ and item.endswith('.log'):
			insar=parser.Parser(full_path)
			sar_viz=viz.Visualization(insar.get_sar_info(),paging=True,network=True,disk=True)
			sar_viz.save(full_path+'.pdf')

if __name__ == '__main__':
	main()
